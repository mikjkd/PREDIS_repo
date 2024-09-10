from injector import Injector


class GlobalInjectorBase:
    def __init__(self):
        self.injector = Injector()
        self.config = None

    def set_config(self, config):
        self.config = config

    def get_device(self):
        return self.injector.get(self.config['device'])

    def get_electronic_api(self):
        return self.injector.get(self.config['electronic_api'])


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GlobalInjector(GlobalInjectorBase, metaclass=Singleton):
    pass
