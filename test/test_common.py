import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestCommon(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get_measures(self):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        scale = 'max'
        type_requested = ['Temperature', 'CO2']
        date_begin = 333
        date_end = 666


        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getmeasure',
                                                     httplib.OK,
                                                     None,
                                                     'api', 'getmeasure', 'GET.json')
        result = self.client.common.get_measure(device_id=device_id,
                                                module_id=module_id,
                                                scale=scale,
                                                measure_types=type_requested,
                                                date_begin=date_begin,
                                                date_end=date_end)
        self.client.get.assert_called_with('https://api.netatmo.net/api/getmeasure',
                                           params=dict(device_id=device_id,
                                                       module_id=module_id,
                                                       scale=scale,
                                                       type=','.join(type_requested),
                                                       date_begin=date_begin,
                                                       date_end=date_end))
        self.assertEqual(len(result), 439)
        for measure in result:
            for value in measure['value']:
                self.assertEqual(len(value), len(type_requested))
