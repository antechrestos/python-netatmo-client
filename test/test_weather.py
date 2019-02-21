import httplib
import unittest

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestWeather(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get_station_data(self):
        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getstationsdata',
                                          httplib.OK,
                                          None,
                                          'api', 'getstationsdata', 'GET.json')
        result = self.client.weather.get_station_data()
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 3)

    def test_get_station_data_by_device(self):
        device_id = 'test-device-id'

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('device_id'), device_id)

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getstationsdata',
                                          httplib.OK,
                                          None,
                                          'api', 'getstationsdata', 'GET_{id}.json')

        result = self.client.weather.get_station_data(device_id=device_id)

        self.client.get.assert_called_with('https://api.netatmo.net/api/getstationsdata',
                                           params=dict(device_id=device_id))

        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 1)
