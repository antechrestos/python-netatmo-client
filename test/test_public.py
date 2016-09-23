import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestStation(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    @mock.patch('netatmo_client.client.requests')
    def test_get_public_data(self, fake_requests):
        lat_ne = 15
        lon_ne = 20
        lat_sw = -15
        lon_sw = -20

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('lat_ne'), lat_ne)
            self.assertEqual(kwargs.get('params').get('lon_ne'), lon_ne)
            self.assertEqual(kwargs.get('params').get('lat_sw'), lat_sw)
            self.assertEqual(kwargs.get('params').get('lon_sw'), lon_sw)

        fake_requests.get = mock_response('https://api.netatmo.net/api/getpublicdata',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'getpublicdata', 'GET.json')
        result = self.client.public.get_public_data(lat_ne, lon_ne, lat_sw, lon_sw)
        self.assertEqual(len(result), 313)
