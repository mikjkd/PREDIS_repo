from datetime import datetime, timedelta
from typing import Dict


class Schedule:
    def __init__(self, measure_time, wakeup_in, start_time_obj, end_time_obj):
        self.measure_time = int(measure_time)  # millisec
        self.wakeup_in = int(wakeup_in)  # minutes
        try:
            # 19-09-18 13:55:26
            self.start_time: datetime = start_time_obj
            self.end_time: datetime = end_time_obj
        except Exception as e:
            print(e)
            self.start_time = None
            self.end_time = None

    def is_valid(self):
        if self.start_time is not None and self.end_time is not None:
            now = datetime.now()
            if (self.start_time < now < self.end_time) and (self.end_time - now).total_seconds() > 0 and (
                    self.end_time - now).total_seconds() > (self.measure_time / 1000):
                return True
            return False
        return False

    def wake_up_at(self):
        r = datetime.now() + timedelta(minutes=self.wakeup_in)
        return [r.strftime('%H'), r.strftime('%M')]

    def to_json(self):
        timeformat = '%d-%m-%y %H:%M'
        return {
            'start_time': '' if self.start_time is None else self.start_time.strftime(timeformat),
            'end_time': '' if self.end_time is None else self.end_time.strftime(timeformat),
            'measure_time': self.measure_time,
            'wakeup_in': self.wakeup_in
        }


class SchedulerBase(object):

    def __init__(self):
        self.devname_schedule: Dict[str, Schedule] = {}

    # salvo in un dizionario la coppia key,val = devname, ip
    # problematica: potrei salvare un devnamey e un ipy, nel momento in cui
    #               questo devname esiste ancora, ma il device in realtà non è
    #               più presente nella rete, ipy potrebbe essere assegnato dal DHCP
    #               ad un nuovo device con devnameK. di conseguenza avrei nella mappa
    #               qualcosa come devnameY, ipY e devnameK, ipY
    #               devo poter fare un doppio controllo, come ad esempio vedere se l'ip
    #               già esiste, in tal caso mi fido del DHCP (perchè non assegnerebbe mai lo stesso
    #               ip a due dispositivi presenti in rete) e potrei dire che il devname vecchio
    #               non ha più in un ip.
    def schedule(self, devname, schedule) -> bool:
        if schedule.is_valid():
            self.devname_schedule[devname] = schedule
            return True
        return False

    def to_json(self):
        return [{'devname': k, 'schedule': Scheduler().devname_schedule[k].to_json()} for k in
                Scheduler().devname_schedule.keys()]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Scheduler(SchedulerBase, metaclass=Singleton):
    pass
