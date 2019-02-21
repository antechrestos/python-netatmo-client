import httplib
import unittest

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestPublic(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get_public_data(self):
        lat_ne = 15
        lon_ne = 20
        lat_sw = -15
        lon_sw = -20

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getpublicdata',
                                          httplib.OK,
                                          None,
                                          'api', 'getpublicdata', 'GET.json')

        result = self.client.public.get_public_data(lat_ne, lon_ne, lat_sw, lon_sw)

        self.client.get.assert_called_with('https://api.netatmo.net/api/getpublicdata',
                                           params=dict(lon_ne=lon_ne, lat_sw=lat_sw, lon_sw=lon_sw, lat_ne=lat_ne))
        self.assertEqual(len(result), 313)
