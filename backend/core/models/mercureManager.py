import os
import urllib.parse
from enum import Enum

import requests


class MercureMessage:
    data = None
    private = False
    message_id = None
    event_type = None
    retry = None
    topics = None

    def __init__(self, topics, data, private=False, message_id=None, event_type=None, retry=None):
        """
        Defines a message

        :param list topics:  Which topics this message will be published
        :param str data: Data itself
        :param str private: To mark this update as private. (Optional)
        :param str message_id: The topic's revision identifier: it will be used as the SSE's id property (Optional)
        :param str event_type: The SSE's event property (a specific event type) (Optional)
        :param int retry:  The SSE's retry property (the reconnection time) (Optional)
        """
        self.topics = topics
        self.data = data
        self.private = private
        self.message_id = message_id
        self.event_type = event_type
        self.retry = retry


class MercureEvents(Enum):
    DEV_STATE = "dev_state"
    NEW_MEASURE = "new_measure"


class MercureTopics(Enum):
    DEV_STATE_UPDATE = ['predis_dev_state']
    MEASURE_UPDATE = ['predis_measure_update']
    ALL = ['predis_dev_state', 'predis_measure_update']


class MercureManagerBase:
    message = None

    def __init__(self):
        self.mercure_hub = os.environ.get('MERCURE_HUB')
        self.mercure_token = os.environ.get('MERCURE_TOKEN')
        try:
            res = requests.get(self.mercure_hub, headers=self._get_request_headers(), timeout=5)
            if res.status_code != 400:
                raise Exception(f'impossibile connettersi a mercure')
        except Exception as e:
            raise Exception(f'impossibile connettersi a mercure: {e}')

    def is_mercure_online(self):
        return True

    def _get_request_headers(self) -> object:
        return {
            'Authorization': 'Bearer ' + self.mercure_token,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    @staticmethod
    def _get_form_data(message) -> str:
        """
        Encode the message
        :param Message message:
        :return str
        """
        form_data = {
            'topic': message.topics,
            'data': message.data
        }

        if message.private == True:
            form_data['private'] = "on"

        if message.message_id is not None:
            form_data['id'] = message.message_id

        if message.event_type is not None:
            form_data['type'] = message.event_type
        return urllib.parse.urlencode(form_data, True)

    def publish(self, message: MercureMessage) -> str:
        # Create the request
        response = requests.post(
            self.mercure_hub,
            self._get_form_data(message),
            headers=self._get_request_headers()
        )
        if response.status_code == 403:
            raise Exception(response.text)
        return str(response.text)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MercureManager(MercureManagerBase, metaclass=Singleton):
    pass
