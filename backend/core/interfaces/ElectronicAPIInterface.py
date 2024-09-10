from enum import Enum
from typing import Union

import requests


class ThresholdName(Enum):
    Thr_A = "Thr_A"
    Thr_B = "Thr_B"


class DownloadFileEnum(Enum):
    DwnLastFile = "DwnLastFile"
    DwnFile = "DwnFile"


class HVName(Enum):
    HV = "HV"


class ParamEnum(Enum):
    Thr_A = "objThrsXValIN"  # get?objThrsXValIN=<inputMessage>
    Thr_B = "objThrsYValIN"  # get?objThrsYValIN=<inputMessage>
    HV = "objHVValIN"  # get?objHVValIN=<inputMessage>
    Acq_Time = "objAcqTimeIN"  # get?objAcqTimeIN=<time in ms>
    Pre_Acq_Time = "objPreAcqTimeIN"  # get?objPreAcqTimeIN=<time in ms>
    Curr_Time = "currentTime"  # set RTC Watch with current Time from Browser get?currentTime= <Date and Time in standard iso format> ex:2022-09-23T16:48
    HV_State = "objHVStateIN"  # get?objHVStateIN=<ON / OFF>
    HV_Temp = "objTempHVValIN"  # get?objTempHVValIN=<value integer>
    Pulser_State = "objPulserStateIN"  #
    Pulser_Period = "objPulserPeriodIN"
    Pulser_Width = "objPulsesWidthIN"
    Central_Node_Addr = "CentralNodeAddress"  # get?CentralNodeAddress=172.16.11.189:62869
    Set_Alarm_1H = "alarm1H"  # set RTC Alarm 1 //get?HourAlarm1=<0 - 23>&MinutesAlarm1=<0-59>


class ElectronicAPIInterface:

    # API utilizzate per contattare il dispositivo fisico



    # /Restart
    def restart(self, ip) -> bool:
        pass

    # /DwnLastFile o /DwnFile non posso scaricare un file con un determinato nome
    # posso solo usare gli url definiti sopra per scaricare i due tipi di file
    # DwnLastFile consente di scaricare il "fileConteggi"
    # DwnFile consente di scaricare il file.asc
    def api_download_data(self, ip: str, filetype: Union[DownloadFileEnum, None], filename=None):
        pass

    # /get
    # param SSID
    def set_ssid(self, ip: str, SSID: str) -> bool:
        pass

    # param PWD
    def set_pwd(self, ip: str, PWD: str) -> bool:
        pass

    def shutdown(self, ip):
        pass

    # param DELETEFILE
    def delete_file(self, ip: str, filename: str) -> bool:
        pass

    def set_params(self, ip: str, param: ParamEnum, param_val) -> Union[requests.Response, None]:
        pass

    def set_threshold(self, ip: str, thr_val: int, thr_name: ThresholdName) -> bool:
        pass

    def set_hv_val(self, ip: str, hv_val) -> bool:
        pass

    def set_param_acq_time(self, ip: str, acq_time) -> bool:
        pass

    def set_param_preacq_time(self, ip: str, preacq_time) -> bool:
        pass

    def set_rtc_wakeup(self, ip: str, hour: str, min: str):
        pass

    # registry APIs

    def get_config(self, ip):
        pass

    def turn_on_devices(self):
        pass

    def api_factory_reset(self, ip):
        pass

