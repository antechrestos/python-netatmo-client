from mock import MagicMock
from oauth2_client.credentials_manager import CredentialManager

from netatmo_client.client import NetatmoClient


def mock_netatmo_client_class():
    if not getattr(NetatmoClient, 'CLASS_MOCKED', False):
        mocked_attributes = ['get', 'post', 'patch', 'put', 'delete']

        class MockClass(CredentialManager):
            def __init__(self, *args, **kwargs):
                super(MockClass, self).__init__(*args, **kwargs)
                for attribute in mocked_attributes:
                    setattr(self, attribute, MagicMock())

        NetatmoClient.__bases__ = (MockClass,)
        setattr(NetatmoClient, 'CLASS_MOCKED', True)


class AbstractTestCase(object):
    CLIENT_ID_TEST = 'client_id_test'

    CLIENT_SECRET = 'client_secret_test'

    ACCESS_TOKEN = 'access_token_test'

    REFRESH_TOKEN = 'refresh_token_test'

    @classmethod
    def mock_client_class(cls):
        mock_netatmo_client_class()

    def build_client(self):
        self.client = NetatmoClient(self.CLIENT_ID_TEST, self.CLIENT_SECRET, ['read_station',
                                                                              'read_thermostat',
                                                                              'write_thermostat',
                                                                              'read_camera'])
        self.client._access_token = self.ACCESS_TOKEN
        self.client.refresh_token = self.REFRESH_TOKEN
