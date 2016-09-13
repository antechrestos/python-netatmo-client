import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestStation(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    @mock.patch('netatmo_client.client.requests')
    def test_get_station_data(self, fake_requests):
        fake_requests.get = mock_response('https://api.netatmo.net/api/getstationsdata',
                                          'get',
                                          None,
                                          httplib.OK,
                                          None,
                                          'api', 'getstationsdata', 'GET.json')
        result = self.client.station.get_station_data()
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 3)

    @mock.patch('netatmo_client.client.requests')
    def test_get_station_data_by_device(self, fake_requests):
        device_id = 'test-device-id'

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('device_id'), device_id)

        fake_requests.get = mock_response('https://api.netatmo.net/api/getstationsdata',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'getstationsdata', 'GET_{id}.json')

        result = self.client.station.get_station_data(device_id=device_id)
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 1)
