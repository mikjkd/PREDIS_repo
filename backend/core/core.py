import atexit
import configparser
import json
import logging
import os
import sys
from datetime import datetime
from typing import Union, Dict

import dotenv
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from backend.core.electronicAPI import ElectronicAPI
from backend.core.globalInjector import GlobalInjector
from backend.core.interfaces.DeviceInterface import DeviceInterface, State
from backend.core.interfaces.ElectronicAPIInterface import ElectronicAPIInterface, DownloadFileEnum, ParamEnum
from backend.core.models.configuration import Configuration
from backend.core.models.device import Device
from backend.core.models.mercureManager import MercureManager, MercureMessage, MercureTopics
from backend.core.models.persistenceManager import PersistenceManager
from backend.core.registry import Registry
from backend.core.scheduler import Schedule, Scheduler


class DownloadType:
    def __init__(self, mod, d_type, filename):
        self.mod = mod
        self.type = d_type
        self.filename = filename


class PREDISCore:
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.StreamHandler()])
    dotenv.load_dotenv()
    GlobalInjector().set_config({
        'device': Device,
        'electronic_api': ElectronicAPI
    })

    def __init__(self):

        self.logger = logging.getLogger()
        self.logger.info(f'Starting app in {os.environ.get("APP_MODE")} environment')

        self.config = configparser.ConfigParser()
        config_file = os.environ.get("CONFIG_FILE_PATH") + 'config.ini'
        self.config.read(config_file)

        # dipendenza dal db

        try:
            PersistenceManager().is_db_online()
        except Exception as e:
            self.logger.error(f"Database non collegato {e}")
            sys.exit(-1)

        # dipendenza da mercure

        try:
            MercureManager().is_mercure_online()
        except Exception as e:
            self.logger.error(f"{e}")

        if self.config['devices']['load_from_file'] == "true":
            self.logger.info("Carico da file")
            try:
                l_dev = PersistenceManager().load_devices()
                for dev in l_dev:
                    Registry().register(dev['devname'], f"http://{dev['ip']}:{dev['port']}")
            except Exception as e:
                self.logger.error(e)
        else:
            self.logger.info("Non carico da file")
        # aggiorno lo scheduler
        try:

            self.logger.info(datetime.now())
            scheduled_dev = PersistenceManager().load_scheduler()

            for dev in scheduled_dev:
                if Scheduler().schedule(devname=dev['devname'],
                                        schedule=Schedule(measure_time=dev['measure_time'], wakeup_in=dev['wakeup_in'],
                                                          start_time_obj=dev['start_time'],
                                                          end_time_obj=dev['end_time'])):
                    self.logger.info(f'--------SCHEDULE ADDED for {dev["devname"]} -------')
                else:
                    self.logger.info(f'NO SCHEDULE FOR {dev["devname"]} ------- NOT REGISTERED ')
        except Exception as e:
            self.logger.error(e)

        self.e_api: ElectronicAPIInterface = GlobalInjector().get_electronic_api()
        # set cron job for ping each device
        cron_scheduler = BackgroundScheduler()
        cron_scheduler.add_job(func=self.ping, trigger="interval", seconds=60)
        cron_scheduler.start()
        atexit.register(lambda: cron_scheduler.shutdown())

    @staticmethod
    def create_mercure_devupdate_message(devname, state) -> MercureMessage:
        return MercureMessage(topics=MercureTopics.DEV_STATE_UPDATE.value, data=json.dumps({
            'devname': devname,
            'sate': state
        }))

    @staticmethod
    def create_mercure_measure_message(devname, filename) -> MercureMessage:
        return MercureMessage(topics=MercureTopics.MEASURE_UPDATE.value, data=json.dumps({
            'devname': devname,
            'filename': filename
        }))

    def _core_publish_on_mercure(self, message: MercureMessage):
        try:
            MercureManager().publish(message=message)
        except Exception as e:
            self.logger.error(f'impossibile pushare su mercure - {e}')

    def scheduled_measure(self, devname: str, ip: str):
        # la schedulazione è ancora valida
        if Scheduler().devname_schedule[devname].is_valid():
            retry: bool = True
            num_try: int = 0
            max_try: int = 3
            is_ok: bool = False
            schedule: Schedule = Scheduler().devname_schedule[devname]
            while retry and num_try < max_try:
                # dico al dispositivo di settare i parametri giusti
                # reimposto l'orologio corrente

                p = ParamEnum.Curr_Time
                currtime_val = datetime.now().strftime("%Y-%m-%dT%H:%M")
                # 2023-10-4 15:17
                currtime_val_res = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.e_api.set_params(ip=ip, param=p, param_val=currtime_val)

                # imposto tempo di acquisizione

                p = ParamEnum.Acq_Time
                acqutime_val = schedule.measure_time
                self.e_api.set_params(ip=ip, param=p, param_val=acqutime_val)

                # setto RTC
                h, m = schedule.wake_up_at()
                self.e_api.set_rtc_wakeup(ip, h, m)

                dev_config = self.e_api.get_config(ip=ip)
                if dev_config['JsDailyAlarm'] != f'{h}:{m}':
                    self.logger.debug((dev_config['JsAcqTime'], schedule.measure_time, dev_config['JsCurrentTime'],
                                       currtime_val_res, dev_config['JsDailyAlarm'], f'{h}:{m}'))
                    retry = True
                    num_try = num_try + 1
                    self.logger.info(f"RETRY n {num_try}")
                else:
                    retry = False
                    is_ok = True

            if not is_ok:
                raise Exception('non è possibile cambiare i parametri')
            else:
                dev: DeviceInterface = Registry().devname_devobject_map[devname]
                dev.set_configuration(dev_config)
                self.logger.info(f"device riconfigurato! {dev_config}")
                return True

        else:  # lo schedule è scaduto, imposto un tempo di misura di 1 secondo in modo da non bloccare il device
            retry: bool = True
            num_try: int = 0
            max_try: int = 3
            is_ok: bool = False

            while retry and num_try < max_try:
                # imposto tempo di acquisizione
                p = ParamEnum.Acq_Time
                acqutime_val = 1000
                self.e_api.set_params(ip=ip, param=p, param_val=acqutime_val)
                dev_config = self.e_api.get_config(ip=ip)
                if int(dev_config['JsAcqTime']) != int(acqutime_val):
                    self.logger.debug((int(dev_config['JsAcqTime']), int(acqutime_val)))
                    retry = True
                    num_try = num_try + 1
                    self.logger.info(f"RETRY n {num_try}")
                else:
                    retry = False
                    is_ok = True
            if not is_ok:
                raise Exception('non è possibile resettare i parametri')
            else:
                dev: DeviceInterface = Registry().devname_devobject_map[devname]
                dev.set_configuration(dev_config)
                Scheduler().devname_schedule.pop(devname)
                self.logger.info(f"schedule terminato! {dev_config}")
                return True

    def factory_reset(self, devname: str):
        ip = Registry().get_map()[devname]
        self.logger.info(f'(trying to factory reset  ------- (devname:{devname})')
        self.e_api.api_factory_reset(ip=ip)
        dev: DeviceInterface = Registry().devname_devobject_map[devname]
        dev.set_state(State.FR)
        self.logger.info(f'(correctly Reset  ------- (devname:{devname})')
        return True

    def apply_schedule(self, devname):
        try:
            ip = Registry().get_map()[devname]
            # controllo se c'è una misura schedulata, in tal caso setto il dispositvo
            scheduled_dev = PersistenceManager().load_scheduler(devname=devname)
            for dev in scheduled_dev:
                Scheduler().schedule(devname=dev['devname'],
                                     schedule=Schedule(measure_time=dev['measure_time'], wakeup_in=dev['wakeup_in'],
                                                       start_time_obj=dev['start_time'],
                                                       end_time_obj=dev['end_time']))
            if devname in list(Scheduler().devname_schedule.keys()):
                if self.scheduled_measure(devname, ip):
                    # contattare client per dire che la misura è finita
                    self.logger.info(f'devname: {devname} ------- EVENTO SCHEDULATO CON SUCCESSO !!!!!!')
                    return True
        except Exception as e:
            self.logger.error(f'ERRORE : {e}')
            self.logger.info(f'devname: {devname} ------- NON SCHEDULATO')
            return False

    def shutdown(self, devname):
        try:
            ip = Registry().get_map()[devname]
            self.logger.info(f'(trying to shutdown  ------- (devname:{devname})')
            self.e_api.shutdown(ip=ip)
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            dev.set_state(State.Spento)
            self._core_publish_on_mercure(
                message=self.create_mercure_devupdate_message(devname=devname, state=dev.get_state().value))
            self.logger.info(f'(correctly shot down  ------- (devname:{devname})')
            return True
        except Exception as e:
            self.logger.error(f'(not able to shutdown  ------- (devname:{devname}) with error {e}')
            return False

    @staticmethod
    def _ping_dev(dev: DeviceInterface, force) -> State:
        url = dev.get_ip()
        corr_stat: State = dev.get_state()
        # SE il device si accende lo vedo dal Registry. Se si spegne invece, non me me ne rendo conto.
        # per questo motivo, quindi, pingo solo quando so che non è spento e in tal caso, cambio stato.
        if (dev.get_state() != State.Spento and dev.get_state() != State.Misure) or force:
            try:
                requests.get(url, timeout=1.5)
                # è ancora acceso, non tocco nulla
            except Exception:
                # si è spento, aggiorno lo stato
                corr_stat = State.Spento
                dev.set_state(corr_stat)
        return corr_stat

    def ping(self, devname=None, force=False):
        devices = []
        if devname is not None:
            devlist = [Registry().devname_devobject_map[devname]]
        else:
            devlist = list(Registry().devname_devobject_map.values())
        try:
            for dev in devlist:
                devices.append(
                    {
                        'devname': dev.get_name(),
                        'ip': dev.get_ip(),
                        'status': self._ping_dev(dev, force).value
                    }
                )
                self._core_publish_on_mercure(
                    message=self.create_mercure_devupdate_message(devname=dev.get_name(), state=dev.get_state().value))
        except Exception as e:
            self.logger.error(e)
            return None
        self.logger.info(f'pinged correctly)')
        return devices

    @staticmethod
    def get_devices():
        devices = Registry().devname_ip_map
        keys = devices.keys()
        res = []
        for k in keys:
            res.append(
                {
                    'devname': k,
                    'ip': devices[k]
                }
            )
        return res

    def get_device(self, devname: str):
        try:
            device: DeviceInterface = Registry().devname_devobject_map[devname]
            ip = Registry().devname_ip_map[devname]
            config = device.get_configuration().to_json()
            res = {
                'devname': devname,
                'ip': ip,
                'configuration': config
            }
            return res
        except Exception as e:
            self.logger.error(e)
            return None

    def launch_measure(self, devname: str):
        try:
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            ip = Registry().get_map()[devname]
        except Exception as e:
            self.logger.error(e)
            return False
        try:
            # PER MISURARE BISOGNA RIAVVIARE IL DEVICE
            # misure avviate, bisogna aspettare che ricontatta
            if self.e_api.restart(ip):
                dev.set_state(State.Misure)
                self._core_publish_on_mercure(
                    self.create_mercure_devupdate_message(devname=devname, state=dev.get_state().value))
                return True
            else:
                dev.set_state(State.NA)
                self.logger.error("Impossibile riavviare il dispositivo")
                return False

        except Exception as e:
            dev.set_state(State.NA)
            self._core_publish_on_mercure(
                self.create_mercure_devupdate_message(devname=devname, state=dev.get_state().value))
            self.logger.error(f"ERRORE: {e}")
            return False

    def download_data(self, devname: str, download_type: DownloadType, ip=None) -> Union[str, None]:
        if ip is None:
            try:
                ip = Registry().get_map()[devname]
            except Exception as e:
                self.logger.error(f'{devname}: non esistente in map {e}')
                return None
        # download_type può essere conteggi o misure
        if download_type.mod == 'new':
            try:
                if download_type.type == "conteggi":
                    file_name, response_content = self.e_api.api_download_data(ip, DownloadFileEnum.DwnLastFile)
                else:
                    file_name, response_content = self.e_api.api_download_data(ip, DownloadFileEnum.DwnFile)
                return PersistenceManager().save_file(devname=devname, file_name=file_name,
                                                      file_content=response_content)
            except Exception as e:
                self.logger.error(f'ERRORE DOWNLOAD DATA by {devname}: {e}')
                return None
        elif download_type.mod == 'old':
            filename = download_type.filename
            try:
                file_name, response_content = self.e_api.api_download_data(ip, None, filename=filename)
                return PersistenceManager().save_file(devname=devname, file_name=file_name,
                                                      file_content=response_content)
            except Exception as e:
                self.logger.error(f'ERRORE DOWNLOAD DATA by {devname}: {e}')
                return None
        else:
            self.logger.info('Modalità download non conosciuta')
            return None

    def set_parameter(self, devname, param, parameter_val) -> bool:
        try:
            ip = Registry().get_map()[devname]
            self.e_api.set_params(ip=ip, param=param, param_val=parameter_val)
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            # l'oggetto response non contiene tutte le informazioni, le aggiorno tramite l'api get_config
            data = self.e_api.get_config(ip=ip)
            dev.set_configuration(data)
            return True
        except Exception as e:
            self.logger.error(f" cannot set paraemter for device {devname}: {e}")
            return False

    def set_rtc_alarm(self, devname, hour, minutes) -> bool:
        try:
            ip = Registry().get_map()[devname]
            self.e_api.set_rtc_wakeup(ip=ip, hour=hour, min=minutes)
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            # l'oggetto response non contiene tutte le informazioni, le aggiorno tramite l'api get_config
            data = self.e_api.get_config(ip=ip)
            dev.set_configuration(data)
            return True
        except Exception as e:
            self.logger.error(f"Cannot set rtc clock for {devname} ---- {e}")
            return False

    def get_dev_config(self, devname) -> Union[Configuration, None]:
        try:
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            return dev.get_configuration()
        except Exception as e:
            self.logger.error(e)
            return None

    def update_dev_config(self, devname) -> Union[Configuration, None]:
        try:
            ip = Registry().get_map()[devname]
            json_val = self.e_api.get_config(ip=ip)
            self.logger.info(json_val)
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            dev.set_configuration(json_val)
            return dev.get_configuration()
        except Exception as e:
            self.logger.error(e)
            return None

    def get_dev_status(self, devname) -> Union[Dict[str, str], None]:
        try:
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            res = {
                'status': dev.get_state().value
            }
            return res
        except Exception as e:
            self.logger.error(e)
            return None

    # riattivo tutti i dispositivi

    def turn_on_devices(self) -> bool:
        if self.e_api.turn_on_devices():
            self.logger.info('------ ALL DEVICESS WILL BE TURNED ON -------')
            return True
        else:
            self.logger.error('------ CANNOT TURN ON DEVICES -------')
            return False

    # API per device

    def register_device(self, devname, remote_addr, port=None) -> bool:
        if port is None:
            port = 80

        ip = f'http://{remote_addr}:{port}'
        self.logger.info(f'STARTING REGISTRATION   ------- ip: {ip} ------- devname: {devname}')

        try:
            Registry().register(devname, ip)
            dev: DeviceInterface = Registry().devname_devobject_map[devname]
            dev.set_state(State.Idle)
            self._core_publish_on_mercure(
                self.create_mercure_devupdate_message(devname=devname, state=dev.get_state().value))
            try:
                # controllo se c'è una misura schedulata, in tal caso setto il dispositvo
                if devname in list(Scheduler().devname_schedule.keys()):
                    if self.scheduled_measure(devname, ip):
                        # contattare client per dire che la misura è finita
                        self.logger.info(f'devname: {devname} ------- EVENTO SCHEDULATO CON SUCCESSO !!!!!!')
            except Exception as e:
                self.logger.error(f'ERRORE : {e}')
                self.logger.info(f'devname: {devname} ------- NON SCHEDULATO')

            # registro il dispositivo sul file
            # se lo sto caricando da file, non è necessario riscriverlo
            # altrimenti lo sto registra
            dev_config = self.e_api.get_config(ip)
            dev.set_configuration(dev_config)

            db_obj = {
                'dev': {
                    'id': devname,
                    'ip': remote_addr,
                    'port': port,
                    'configid': None
                },
                'config': {"thra": dev_config['JsThrsValX'], "thrb": dev_config['JsThrsValY'],
                           "hv": dev_config['JsHVVal'], "acquisition_time": dev_config['JsAcqTime'],
                           "preacquisition_time": dev_config['JsPreAcqTime'], "alarm": dev_config['JsDailyAlarm'],
                           "curr_datetime": dev_config['JsCurrentTime'],
                           "delay_hv": None}
            }

            try:
                PersistenceManager().save_device(dev=db_obj['dev'], config=db_obj['config'])
            except Exception as e:
                self.logger.error(e)
            try:
                content = [devname, datetime.now().strftime('%Y-%m-%d %H:%M'), dev.get_configuration().acquisition_time,
                           dev.get_configuration().daily_alarm]
                PersistenceManager().journal(content)
            except Exception as e:
                self.logger.error(f'Error to journal {e}')
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    # quando un dispositivo è pronto, può contattare il backend per comunicargli la
    # possibilità di un nuovo scarico
    # deve essere implementata come API in flask
    def data_is_ready(self, remote_addr, port=None) -> bool:
        if port is None:
            port = 80
        # posso anche non utilizzare il devname dato che è possibile contattare
        # il dispositivo per ottenere i dati senza passare per il devname
        # però è corretto in quanto posso aggiornare delle informazioni
        # ad es. posso salvare sull'oggetto dispositivo il timestamp dell'ultimo donwload
        # oppure posso informare il filemanager del fatto che sta salvando il file di un
        # determinato di spositivo D
        # ottengo quindi il devname a partire dall'ip
        ip = f'http://{remote_addr}:{port}'
        devname = Registry().ip_devname_map[ip]
        self.logger.info(f'(ip: {ip}, devname: {devname})  ------- has data ready  ------- ')
        download_type: DownloadType = DownloadType(mod='new', d_type=None, filename=None)
        try:
            self.logger.info(f'(ip: {ip}, devname: {devname})  ------- trying to download Conteggi  ------- ')
            download_type.type = 'conteggi'
            conteggi_filename = self.download_data(devname=devname, download_type=download_type, ip=ip)
            self.logger.info(f'(ip: {ip}, devname: {devname})  ------- CONTEGGI download completed  ------- ')
            try:
                # salvo la misura sul DB
                db_obj = PersistenceManager().convert_PREDIS_data(conteggi_filename)
                PersistenceManager().save_measure_to_db(measure_obj=db_obj)
                self.logger.info(f'(ip: {ip}, devname: {devname})  ------- CONTEGGI salvato su db  ------- ')
                self._core_publish_on_mercure(
                    message=self.create_mercure_measure_message(devname=devname, filename=conteggi_filename))
            except Exception as e:
                self.logger.error(f'ERRORE salvataggio misure sul db: {e}')
        except Exception as e:
            self.logger.error(f'ERRORE Download file conteggi: {e}')
        try:
            self.logger.info(f'(ip: {ip}, devname: {devname})  ------- trying to download Misure  ------- ')
            download_type.type = 'misure'
            if self.download_data(devname=devname, download_type=download_type, ip=ip) is not None:
                self.logger.info(f'(ip: {ip}, devname: {devname})  ------- MISURE download completed  ------- ')
        except Exception as e:
            self.logger.error(f'ERRORE Download file misure: {e}')

        return True

    def get_loaded_schedule(self):
        return Scheduler().to_json()
