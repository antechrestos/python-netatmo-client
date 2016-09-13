import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestThermostat(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    @mock.patch('netatmo_client.client.requests')
    def test_get_thermostat_data(self, fake_requests):
        fake_requests.get = mock_response('https://api.netatmo.net/api/getthermostatsdata',
                                          'get',
                                          None,
                                          httplib.OK,
                                          None,
                                          'api', 'getthermostatsdata', 'GET.json')
        result = self.client.thermostat.get_thermostat_data()
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 2)

    @mock.patch('netatmo_client.client.requests')
    def test_get_thermostat_data_by_device(self, fake_requests):
        device_id = 'test-device-id'

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('device_id'), device_id)

        fake_requests.get = mock_response('https://api.netatmo.net/api/getthermostatsdata',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'getthermostatsdata', 'GET_{id}.json')

        result = self.client.thermostat.get_thermostat_data(device_id=device_id)
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 1)

    @mock.patch('netatmo_client.client.requests')
    def test_create_schedule(self, fake_requests):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        name = 'test-name-id'

        def _check_form(**kwargs):
            self.assertIsNotNone(kwargs.get('data'))
            form = kwargs.get('data')
            self.assertEqual(form.get('device_id'), device_id)
            self.assertEqual(form.get('module_id'), module_id)
            self.assertEqual(form.get('name'), name)
            self.assertIsNotNone(form.get('zones'))
            self.assertIsNotNone(form.get('timetable'))

        fake_requests.post = mock_response('https://api.netatmo.net/api/createnewschedule',
                                           'post',
                                           _check_form,
                                           httplib.OK,
                                           None,
                                           'api', 'createnewschedule', 'POST.json')

        result = self.client.thermostat.create_new_schedule(device_id=device_id,
                                                            module_id=module_id,
                                                            name=name,
                                                            zones=[],
                                                            timetable=[])
        self.assertEqual(result['schedule_id'], '53a056ba55ee4f57198b4569')

    @mock.patch('netatmo_client.client.requests')
    def test_set_therm_point(self, fake_requests):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        setpoint_mode = 'manual'
        setpoint_endtime = 666
        setpoint_temp = 19

        def _check_form(**kwargs):
            self.assertIsNotNone(kwargs.get('data'))
            form = kwargs.get('data')
            self.assertEqual(form.get('device_id'), device_id)
            self.assertEqual(form.get('module_id'), module_id)
            self.assertEqual(form.get('setpoint_mode'), setpoint_mode)
            self.assertEqual(form.get('setpoint_endtime'), setpoint_endtime)
            self.assertEqual(form.get('setpoint_temp'), setpoint_temp)

        fake_requests.post = mock_response('https://api.netatmo.net/api/setthermpoint',
                                           'post',
                                           _check_form,
                                           httplib.OK,
                                           None,
                                           'api', 'setthermpoint', 'POST.json')

        self.client.thermostat.set_therm_point(device_id=device_id,
                                               module_id=module_id,
                                               setpoint_mode=setpoint_mode,
                                               setpoint_endtime=setpoint_endtime,
                                               setpoint_temp=setpoint_temp)

    @mock.patch('netatmo_client.client.requests')
    def test_switch_schedule(self, fake_requests):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        schedule_id = 'test-schedule-id'

        def _check_form(**kwargs):
            self.assertIsNotNone(kwargs.get('data'))
            form = kwargs.get('data')
            self.assertEqual(form.get('device_id'), device_id)
            self.assertEqual(form.get('module_id'), module_id)
            self.assertEqual(form.get('schedule_id'), schedule_id)

        fake_requests.post = mock_response('https://api.netatmo.net/api/switchschedule',
                                           'post',
                                           _check_form,
                                           httplib.OK,
                                           None,
                                           'api', 'switchschedule', 'POST.json')

        self.client.thermostat.switch_schedule(device_id=device_id,
                                               module_id=module_id,
                                               schedule_id=schedule_id)

    @mock.patch('netatmo_client.client.requests')
    def test_sync_schedule(self, fake_requests):
        device_id = 'test-device-id'
        module_id = 'test-module-id'

        def _check_form(**kwargs):
            self.assertIsNotNone(kwargs.get('data'))
            form = kwargs.get('data')
            self.assertEqual(form.get('device_id'), device_id)
            self.assertEqual(form.get('module_id'), module_id)
            self.assertIsNotNone(form.get('zones'))
            self.assertIsNotNone(form.get('timetable'))

        fake_requests.post = mock_response('https://api.netatmo.net/api/syncschedule',
                                           'post',
                                           _check_form,
                                           httplib.OK,
                                           None,
                                           'api', 'syncschedule', 'POST.json')

        self.client.thermostat.sync_schedule(device_id=device_id,
                                             module_id=module_id,
                                             zones=[],
                                             timetable=[])
