import json
import unittest

import dotenv

from codice.backend.core.models.mercureManager import MercureManager, MercureMessage


class MyTestCase(unittest.TestCase):
    def test_mercure_connection(self):
        dotenv.load_dotenv('../core/.env')
        print(MercureManager().is_mercure_online())

    def test_mercure_publish(self):
        dotenv.load_dotenv('../core/.env')
        topic = 'predis_dev_state'
        data = {
            'devname': 'PREDIS010',
            'state': 'online'
        }
        msg = MercureMessage(topics=[topic], data=json.dumps(data))
        MercureManager().publish(message=msg)


if __name__ == '__main__':
    unittest.main()
