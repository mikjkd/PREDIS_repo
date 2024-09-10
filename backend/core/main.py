# esempio di main senza utilizzo di flask
from codice.backend.core.electronicAPI import ElectronicAPI
from codice.backend.core.globalInjector import GlobalInjector
from codice.backend.core.interfaces.DeviceInterface import DeviceInterface
from codice.backend.core.models.device import Device
from codice.backend.core.registry import Registry

if __name__ == '__main__':
    # bisogna injectare la dipendenza in device
    GlobalInjector().set_config({
        'device': Device,
        'electronic_api': ElectronicAPI
    })
    Registry().register('dev0', 'http://localhost:1234')
    dev0: DeviceInterface = Registry().devname_devobject_map['dev0']
    #dev0.set_ssid('a', 'b')

    #print(dev0.get_config())
    #print(dev0.download_data())
