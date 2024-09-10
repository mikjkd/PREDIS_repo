class Configuration:
    def __init__(self):
        self.DAC_threshold_A = None
        self.DAC_threshold_B = None
        self.DAC_HV = None
        self.acquisition_time = None
        self.preacquisition_time = None
        self.delay_HV = None
        self.time = None
        self.daily_alarm = None

    def set_configuration(self, data):
        self.DAC_threshold_A = data['JsThrsValX'] if 'JsThrsValX' in data else self.DAC_threshold_A
        self.DAC_threshold_B = data['JsThrsValY'] if 'JsThrsValY' in data else self.DAC_threshold_B
        self.DAC_HV = data['JsHVVal'] if 'JsHVVal' in data else self.DAC_HV
        self.acquisition_time = data['JsAcqTime'] if 'JsAcqTime' in data else self.acquisition_time
        self.preacquisition_time = data['JsPreAcqTime'] if 'JsPreAcqTime' in data else self.preacquisition_time
        self.daily_alarm = data['JsDailyAlarm'] if 'JsDailyAlarm' in data else self.daily_alarm
        self.time = data['JsCurrentTime'] if 'JsCurrentTime' in data else self.time

    def to_json(self):
        return {
            "DAC_threshold_A": self.DAC_threshold_A,
            "DAC_threshold_B": self.DAC_threshold_B,
            "DAC_HV": self.DAC_HV,
            "acquisition_time": self.acquisition_time,
            "preacquisition_time": self.preacquisition_time,
            "delay_HV": self.delay_HV,
            "time": self.time,
            "daily_alarm": self.daily_alarm
        }
