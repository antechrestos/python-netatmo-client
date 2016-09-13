import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestStation(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    @mock.patch('netatmo_client.client.requests')
    def test_get_measures(self, fake_requests):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        scale = 'max'
        type_requested = ['Temperature', 'CO2']
        date_begin = 333
        date_end = 666

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('device_id'), device_id)
            self.assertEqual(kwargs.get('params').get('module_id'), module_id)
            self.assertEqual(kwargs.get('params').get('scale'), scale)
            self.assertEqual(kwargs.get('params').get('type'), ','.join(type_requested))
            self.assertEqual(kwargs.get('params').get('date_begin'), date_begin)
            self.assertEqual(kwargs.get('params').get('date_end'), date_end)

        fake_requests.get = mock_response('https://api.netatmo.net/api/getmeasure',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'getmeasure', 'GET.json')
        result = self.client.common.get_measure(device_id=device_id,
                                                module_id=module_id,
                                                scale=scale,
                                                measure_types=type_requested,
                                                date_begin=date_begin,
                                                date_end=date_end)
        self.assertEqual(len(result), 439)
        for measure in result:
            for value in measure['value']:
                self.assertEqual(len(value), len(type_requested))

