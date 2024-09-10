from injector import inject

from codice.backend.core.interfaces.DeviceInterface import DeviceInterface, State
from codice.backend.core.models.configuration import Configuration
from codice.backend.core.models.coords import Coords


# S0 = Spento
# S1 = Misura
# S3 = IDLE


class Device(DeviceInterface):

    @inject
    def __init__(self):
        self.name: str = ''
        self.static_ip: str = ''
        self.mac: str
        self.coords: Coords or None = None
        self.configuration: Configuration or None = Configuration()
        self.state = State.Idle

        print(f'creato nuovo device con id: {id(self)}')

    def create_device(self):
        return Device()

    def set_value(self, name, static_ip):
        self.name = name
        self.static_ip = static_ip

    def set_coords(self, coords):
        self.coords = coords

    def set_config(self, config):
        self.configuration = config

    def get_device(self):
        return self

    def set_configuration(self, cofnig):
        self.configuration.set_configuration(cofnig)

    def get_configuration(self) -> Configuration:
        return self.configuration

    def get_state(self) -> State:
        return self.state

    def set_state(self, new_state: State):
        self.state = new_state

    def get_name(self):
        return self.name

    def get_ip(self):
        return self.static_ip
