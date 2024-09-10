import csv
import os
from datetime import datetime
from typing import Dict, List

from deprecated import deprecated
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.dialects.postgresql import insert


class PersistenceManagerBase:

    def __init__(self):
        self.base_path = f"{os.environ.get('FILE_BASE_PATH')}/"
        self.db_name = os.environ.get('DB_NAME')
        self.db_user = os.environ.get('DB_USER')
        self.db_pass = os.environ.get('DB_PASSWORD')
        self.db_host = os.environ.get('DB_HOST')
        self.db_port = os.environ.get('DB_PORT')
        self.db_string = f'postgresql+psycopg2://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}'
        try:
            self.engine = create_engine(self.db_string)
            self.conn = self.engine.connect()
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
        except Exception as e:
            raise Exception(f'impossibile connettersi al db: {e}')

    def is_db_online(self):
        return True

    def convert_PREDIS_data(self, f):
        header = ['date', 'time', 'deviceid', 'temperature_s1', 'temperature_s2', 'set_acq_time', 'eff_acq_time',
                  'set_hv',
                  'curr_hv', 'no_data', 'current', 'tha', 'thb', 'cha_count', 'chb_count', 'count_coincidences',
                  'analyzed_coincidences']
        f_hanlder = open(f, "r")
        # data.append(f_hanlder.read())
        data = f_hanlder.read()
        sdata = data.split('\n')
        all_data = []
        for d in sdata:
            if d != "":
                all_data.extend(d.split())
        date_time = all_data[0]
        date_time = date_time.split('_')
        date_time[1] = date_time[1].replace('-', ':')
        all_data[0] = datetime.strptime(date_time[0], '%y-%m-%d').strftime('%Y-%m-%d')
        all_data.insert(1, date_time[1])
        all_data[2] = f'PREDIS{all_data[2]}'
        all_data[3:] = [int(i) for i in all_data[3:]]
        all_data.insert(3, 0)
        return {header[idx]: elem for idx, elem in enumerate(all_data)}

    # salva il file di misura appena scaricato dal device
    def save_file(self, devname, file_name, file_content) -> str:
        # f'{os.path.abspath("../../devices")}/'
        if not os.path.isdir(self.base_path + devname):
            os.mkdir(self.base_path + devname)
        filepath = f'{self.base_path + devname}/{file_name}'
        with open(filepath, 'wb') as newfile:
            newfile.write(file_content)
        return filepath

    """
        measure_obj={
            'date':, 
            'time':, 
            'deviceid':, 
            'temperature_s1':,
            'temperature_s2':, 
            'set_acq_time':, 
            'eff_acq_time':, 
            'set_hv':,
            'curr_hv':, 
            'no_data':,
            'current':, 
            'tha':, 
            'thb':, 
            'cha_count':, 
            'chb_count':, 
            'conut_coincidences':,
            'analyzed_coincidences':
        }
    """

    def save_measure_to_db(self, measure_obj):
        measure_table = Table('measure', self.metadata, autoload_with=self.engine)

        stmt = insert(measure_table).values(measure_obj).returning(measure_table.c.id)
        res = self.conn.execute(stmt)
        res_id = res.fetchone()[0]
        self.conn.commit()

        return res_id

    """
    usage:
        filename -> devices.csv
        devices -> [
                        { 'devname':'dev0', 'ip':'192.168.1.1', 'config':'{...}' },
                        { 'devname':'dev1', 'ip':'192.168.1.2', 'config':'{...}' },
                        { 'devname':'dev2', 'ip':'192.168.1.3', 'config':'{...}' }
                    ]
    """

    @deprecated
    def save_devices_to_file(self, filename, device):
        header = ['devname', 'ip']
        devices = [device]
        if os.path.exists(filename):
            # se già esiste devo leggere il file, capire se ci sono dei device già esisteni e modificarli
            rows = self.load_devices_from_file(filename)
            # aggiorno le informazioni
            if len(rows) > 0:
                new_devices = rows
                trovato = False
                for r in new_devices:
                    if r['devname'] in device['devname']:
                        r['ip'] = device['ip']
                        trovato = True
                        break
                if not trovato:
                    new_devices.append(device)

                # aggiorno i devices da scrivere
                devices = new_devices

            # elimino il vecchio file
            new_filename = f"{filename.split('.csv')[0]}_old.csv"
            os.rename(filename, new_filename)
        # se il file non esiste, mi basta scrivere tutto sul file
        mode = 'w'
        with open(filename, mode, newline="") as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(header)
            for dev in devices:
                csvwriter.writerow([dev['devname'], dev['ip']])
        return True

    """
        'dev':{
            'id':'XXXX',
            'ip':'yyyy',
            'port':80,
            'configid':X
            
        }
        'config': {"thra": 200, "thrb": 200, "hv": 1300, "acquisition_time": 10000,
                       "preacquisition_time": 15000, "alarm": "11:30", "curr_datetime": "2023-10-4 15:17",
                       "delay_hv": None}
    """

    def save_device(self, dev: Dict, config: Dict):
        device_table = Table('device', self.metadata, autoload_with=self.engine)
        config_table = Table('config', self.metadata, autoload_with=self.engine)

        stmt = insert(config_table).values(config).returning(config_table.c.id)
        res = self.conn.execute(stmt)
        res_id = res.fetchone()[0]
        dev['configid'] = res_id
        stmt = insert(device_table).values(dev).returning(device_table.c.id)
        # upsert
        stmt = stmt.on_conflict_do_update(
            index_elements=[device_table.c.id],
            set_=stmt.excluded
        )
        res = self.conn.execute(stmt)
        res_dev_id = res.fetchone()[0]
        self.conn.commit()
        return [res_id, res_dev_id]

    @deprecated
    def load_devices_from_file(self, filename):
        rows = []
        with open(filename, 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            for row in csvreader:
                rows.append(
                    {
                        'devname': row[0],
                        'ip': row[1],
                    }
                )
        return rows

    def load_devices(self) -> List[Dict]:
        device_table = Table('device', self.metadata, autoload_with=self.engine)
        stmt = select(device_table.c.id, device_table.c.ip, device_table.c.port)
        res = self.conn.execute(stmt)
        list_res = list(res.fetchall())
        self.conn.commit()
        res_obj = [{
            'devname': l[0].strip(),
            'ip': l[1].strip(),
            'port': l[2]
        } for l in list_res]
        return res_obj

    @deprecated
    def old_load_scheduler(self, filename):
        rows = []
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                csvreader = csv.reader(file)
                header = next(csvreader)
                for row in csvreader:
                    rows.append(
                        {
                            'devname': row[0],
                            'measure_time': row[1],
                            'wakeup_in': row[2],
                            'to': row[3]
                        }
                    )
            return rows
        else:
            return rows

    def load_scheduler(self, devname=None):
        dev_schedule_table = Table('device_schedule', self.metadata, autoload_with=self.engine)
        schedule_table = Table('schedule', self.metadata, autoload_with=self.engine)
        if devname is None:
            stmt = select(
                dev_schedule_table.c.deviceid,
                schedule_table.c.start_ts,
                schedule_table.c.end_ts,
                schedule_table.c.wake_up_every,
                schedule_table.c.measure_time_ms).join(
                dev_schedule_table, dev_schedule_table.c.scheduleid == schedule_table.c.id,
                isouter=False
            )
        else:
            stmt = select(
                dev_schedule_table.c.deviceid,
                schedule_table.c.start_ts,
                schedule_table.c.end_ts,
                schedule_table.c.wake_up_every,
                schedule_table.c.measure_time_ms).join(
                dev_schedule_table, dev_schedule_table.c.scheduleid == schedule_table.c.id,
                isouter=True
            ).where(dev_schedule_table.c.deviceid == devname)
        res = self.conn.execute(stmt)
        list_res = list(res.fetchall())
        self.conn.commit()
        res_obj = [{
            'devname': l[0].strip(),
            'start_time': l[1],
            'end_time': l[2],
            'wakeup_in': l[3],
            'measure_time': l[4]
        } for l in list_res]
        return res_obj

    @deprecated
    def old_journal(self, content):
        base_path = f"{os.environ.get('FILE_BASE_PATH')}/journal.csv"
        head = ['devname', 'timestamp', 'duration', 'wakeup_at']
        exist = True
        if not os.path.exists(base_path):
            exist = False
        with open(base_path, "a+", newline='') as file:
            writer = csv.writer(file)
            if not exist:
                writer.writerow(head)
            writer.writerow(content)

    def journal(self, content):
        db_obj = {
            'deviceid': content[0],
            'timestamp': content[1],
            'duration': content[2],
            'will_wakeup_at': content[3]
        }
        journal_table = Table('event', self.metadata, autoload_with=self.engine)
        stmt = insert(journal_table).values(db_obj).returning(journal_table.c.id)
        res = self.conn.execute(stmt)
        list_res = res.fetchone()[0]
        self.conn.commit()
        return list_res


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PersistenceManager(PersistenceManagerBase, metaclass=Singleton):
    pass
