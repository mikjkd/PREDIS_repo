from enum import Enum

from backend.core.models.configuration import Configuration


class State(Enum):
    Spento = "Spento"
    Misure = "Misura"
    Idle = "Idle"
    NA = "Non Disponibile"
    FR = "Factory Reset"


class DeviceInterface:
    def set_value(self, name, static_ip):
        pass

    def set_coords(self, coords):
        pass

    def set_config(self, config):
        pass

    def get_device(self):
        pass

    def create_device(self):
        pass

    def set_configuration(self, config):
        pass

    def get_configuration(self) -> Configuration:
        pass

    def get_state(self) -> State:
        pass

    def set_state(self, new_state: State):
        pass

    def get_name(self):
        pass

    def get_ip(self):
        pass
