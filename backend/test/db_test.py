import unittest

import dotenv

from codice.backend.core.models.persistenceManager import PersistenceManager


class DBTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_insert(self):
        dev_obj = {
            'dev': {
                'id': 'PREDISX2',
                'ip': '192.168.3.3',
                'port': 12,
                'configid': None
            },
            'config': {"thra": 200, "thrb": 200, "hv": 1300, "acquisition_time": 10000,
                       "preacquisition_time": 15000, "alarm": "11:30", "curr_datetime": "2023-10-4 15:17",
                       "delay_hv": None}
        }
        dotenv.load_dotenv('../core/.env')
        PersistenceManager().save_device(
            dev=dev_obj['dev'],
            config=dev_obj['config']
        )

    def test_load_devices(self):
        dotenv.load_dotenv('../core/.env')
        devices = PersistenceManager().load_devices()
        for dev in devices:
            print(dev['devname'], f"http://{dev['ip']}:{dev['port']}")

    def test_load_scheduler(self):
        dotenv.load_dotenv('../core/.env')
        schedules = PersistenceManager().load_scheduler()
        for schedule in schedules:
            print(schedule)

    def test_load_device_scheduler(self):
        dotenv.load_dotenv('../core/.env')
        schedules = PersistenceManager().load_scheduler(devname='PREDIS22')
        for schedule in schedules:
            print(schedule)

    def test_convert_data(self):
        dotenv.load_dotenv('../core/.env')
        filename = 'dati/abc'
        obj = PersistenceManager().convert_PREDIS_data(filename)
        print(obj)

    def test_save_measure(self):
        dotenv.load_dotenv('../core/.env')
        filename = 'dati/abc'
        obj = PersistenceManager().convert_PREDIS_data(filename)
        PersistenceManager().save_measure_to_db(obj)

if __name__ == '__main__':
    unittest.main()
