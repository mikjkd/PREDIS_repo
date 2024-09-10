from typing import Union

import requests

from backend.core.interfaces.ElectronicAPIInterface import DownloadFileEnum, ParamEnum, ThresholdName
from backend.core.interfaces.ElectronicAPIInterface import ElectronicAPIInterface


class ElectronicAPI(ElectronicAPIInterface):
    def __init__(self):
        pass

    def restart(self, ip) -> bool:
        url = ip + '/Restart'
        response = requests.get(url)
        if response.status_code == 200:
            return True
        return False

    def api_download_data(self, ip, filetype: Union[DownloadFileEnum, None], filename=None):
        if filename is None:
            url = ip + f'/{filetype.value}'
        else:
            url = ip + f'/{filename}'
        response = requests.get(url)
        if response.status_code == 200:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1].replace('"', '')
            response.close()
            return file_name, response.content
        else:
            raise Exception('Errore download file')

    def shutdown(self, ip) -> bool:
        url = ip + '/Shutdown'
        response = requests.get(url)
        if response.status_code == 200:
            return True
        return False

    # param DELETEFILE
    def delete_file(self, ip: str, filename: str) -> bool:
        url = f'{ip}/deletefile?{filename}'
        response = requests.get(url)
        if response.status_code != 200:
            return False
        return True

    def set_params(self, ip: str, param: ParamEnum, param_val) -> Union[requests.Response, None]:
        url = f'{ip}/get?{param.value}={param_val}'
        response = requests.get(url)
        try:
            if response.status_code != 200:
                return None
            return response
        except Exception:
            raise

    # GET input1 value on <ESP_IP>/get?objThrsXValIN=<inputMessage>
    def set_threshold(self, ip: str, thr_val: int, thr_name: ThresholdName) -> bool:

        if thr_name == ThresholdName.Thr_A.value:
            val = ParamEnum.Thr_A
        elif thr_name == ThresholdName.Thr_B.value:
            val = ParamEnum.Thr_B
        else:
            return False
        self.set_params(ip=ip, param=val, param_val=thr_val)
        return True

    def set_hv_val(self, ip: str, hv_val) -> bool:
        self.set_params(ip=ip, param=ParamEnum.HV, param_val=hv_val)
        return True

    def set_param_acq_time(self, ip: str, acq_time) -> bool:
        self.set_params(ip=ip, param=ParamEnum.Acq_Time, param_val=acq_time)
        return True

    def set_param_preacq_time(self, ip, preacq_time) -> bool:
        self.set_params(ip=ip, param=ParamEnum.Pre_Acq_Time, param_val=preacq_time)
        return True

    def set_rtc_wakeup(self, ip: str, hour: str, min: str) -> Union[requests.Response, None]:
        url = f'{ip}/get?alarm1H={hour}&alarm1m={min}'
        response = requests.get(url)
        try:
            if response.status_code != 200:
                return None
            return response
        except Exception as e:
            raise e

    def get_config(self, ip):
        x = requests.get(f'{ip}/parametersReq', timeout=5)
        return x.json()

    def turn_on_devices(self) -> bool:
        # il dongle wifi ha l'ip statico
        ip = "http://192.168.2.29/WUSystem"
        try:
            x = requests.get(ip, timeout=5)
            if x.status_code == 200:
                return True
            return False
        except Exception as e:
            return False

    def api_factory_reset(self, ip):
        url = f'{ip}/FactoryReset'
        try:
            # con il Factory Reset il dispositivo si spegne, quindi la chiamata andrà in timeout
            requests.get(url, timeout=1)
            return True
        except:
            return True
