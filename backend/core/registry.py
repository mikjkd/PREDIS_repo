from backend.core.globalInjector import GlobalInjector
from backend.core.interfaces.DeviceInterface import DeviceInterface, State


class DevMap:
    def __init__(self):
        self.ip = None
        self.devname = None
        self.port = None


class RegistryBase(object):

    def __init__(self):
        self.devname_ip_map = {}
        self.ip_devname_map = {}
        self.devname_devobject_map = {}  # contiene l'istanza che punta al device

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
    def register(self, devname, ip):
        if devname not in self.devname_ip_map:
            if ip in self.ip_devname_map:
                # a questo ip cambio devname
                # vedere se l'ip con cui mi contatta già esiste, in tal caso il vecchio device perde l'ip ed il nuovo lo ottiene
                # altrimenti non tocco gli ip
                old_devname = self.ip_devname_map[ip]
                self.devname_ip_map[old_devname] = None
            self.ip_devname_map[ip] = devname
            self.devname_ip_map[devname] = ip
            # creo nuovo device con questo devname
            device: DeviceInterface = GlobalInjector().get_device()

            device.set_value(name=devname, static_ip=ip)
            device.set_state(State.NA)
            self.devname_devobject_map[devname] = device

        else:
            if self.devname_ip_map[devname] == ip:
                pass
            else:
                if ip in self.ip_devname_map:
                    # a questo ip cambio devname
                    # vedere se l'ip con cui mi contatta già esiste, in tal caso il vecchio device perde l'ip ed il nuovo lo ottiene
                    # altrimenti non tocco gli ip
                    old_devname = self.ip_devname_map[ip]
                    self.devname_ip_map[old_devname] = None
                self.devname_ip_map[devname] = ip
                self.ip_devname_map[ip] = devname
                self.devname_devobject_map[devname].set_value(name=devname, static_ip=ip)

    def get_map(self):
        return self.devname_ip_map

    def get_ip_map(self):
        return self.ip_devname_map


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Registry(RegistryBase, metaclass=Singleton):
    pass
