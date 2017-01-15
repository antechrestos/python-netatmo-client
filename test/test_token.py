import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response, load_resource_path


class TestToken(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    @mock.patch('netatmo_client.client.requests')
    def test_get_thermostat_data(self, fake_requests):
        def _check_request(**kwargs):
            self.assertIsNotNone(kwargs.get('data', None))
            form = kwargs['data']
            self.assertIsInstance(form, dict)
            raw_data_content = load_resource_path(False, 'oauth2', 'token', 'client_credentials.txt')
            data_content = {d[0]: d[1] for d in [c.split("=") for c in raw_data_content.split("&")] if len(d) == 2}
            for k, v in data_content.items():
                self.assertEqual(v, form[k])

        fake_requests.post = mock_response('https://api.netatmo.com/oauth2/token',
                                           'post',
                                           _check_request,
                                           httplib.OK,
                                           None,
                                           'oauth2', 'token', 'POST.json')
        self.client.request_token_with_client_credentials("username@somewhere.com",
                                                          "5\\r{SM0_~gpG",
                                                          "read_station", "read_thermostat")
        self.assertEqual(self.client._access_token, 'the_access_token')
        self.assertEqual(self.client._refresh_token, 'the_refresh_token')
