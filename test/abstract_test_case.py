from netatmo_client.client import NetatmoClient


class AbstractTestCase(object):
    CLIENT_ID_TEST = 'client_id_test'

    CLIENT_SECRET = 'client_secret_test'

    ACCESS_TOKEN = 'access_token_test'

    REFRESH_TOKEN = 'refresh_token_test'

    def build_client(self):
        self.client = NetatmoClient(self.CLIENT_ID_TEST, self.CLIENT_SECRET)
        self.client._access_token = self.ACCESS_TOKEN
        self.client._refresh_token = self.REFRESH_TOKEN
