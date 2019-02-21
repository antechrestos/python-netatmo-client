import httplib
import unittest

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestThermostat(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get_home_data(self):
        self.client.get.return_value = mock_response('https://api.netatmo.net/api/homesdata',
                                                     httplib.OK,
                                                     None,
                                                     'api', 'homesdata', 'GET.json')
        result = self.client.energy.get_home_data(None, 'NaCamera', 'NaPlug')

        self.client.get.assert_called_with('https://api.netatmo.net/api/homesdata',
                                           params=dict(gateway_type='NaCamera,NaPlug'))
        self.assertEqual(len(result['homes']), 2)
        self.assertEqual(len(result['homes'][0]['modules']), 1)
        self.assertEqual(len(result['homes'][1]['modules']), 2)



    def test_get_thermostat_data(self):
        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getthermostatsdata',
                                                     httplib.OK,
                                                     None,
                                                     'api', 'getthermostatsdata', 'GET.json')
        result = self.client.energy.get_thermostat_data()
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 2)

    def test_get_thermostat_data_by_device(self):
        device_id = 'test-device-id'

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getthermostatsdata',
                                                     httplib.OK,
                                                     None,
                                                     'api', 'getthermostatsdata', 'GET_{id}.json')

        result = self.client.energy.get_thermostat_data(device_id=device_id)
        self.client.get.assert_called_with('https://api.netatmo.net/api/getthermostatsdata',
                                           params=dict(device_id=device_id))
        self.assertEqual(result['user']['mail'], 'someone@somewhere.com')
        self.assertEqual(len(result['devices']), 1)

    def test_create_schedule(self):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        name = 'test-name-id'

        self.client.post.return_value = mock_response('https://api.netatmo.net/api/createnewschedule',
                                                      httplib.OK,
                                                      None,
                                                      'api', 'createnewschedule', 'POST.json')

        result = self.client.energy.create_new_schedule(device_id=device_id,
                                                        module_id=module_id,
                                                        name=name,
                                                        zones=[],
                                                        timetable=[])
        self.client.post.assert_called_with('https://api.netatmo.net/api/createnewschedule',
                                            data=dict(device_id=device_id, module_id=module_id,
                                                      name=name, zones='[]', timetable='[]'),
                                            json=None)
        self.assertEqual(result['schedule_id'], '53a056ba55ee4f57198b4569')

    def test_set_therm_point(self):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        setpoint_mode = 'manual'
        setpoint_endtime = 666
        setpoint_temp = 19

        self.client.post.return_value = mock_response('https://api.netatmo.net/api/setthermpoint',
                                                      httplib.OK,
                                                      None,
                                                      'api', 'setthermpoint', 'POST.json')

        self.client.energy.set_therm_point(device_id=device_id,
                                           module_id=module_id,
                                           setpoint_mode=setpoint_mode,
                                           setpoint_endtime=setpoint_endtime,
                                           setpoint_temp=setpoint_temp)
        self.client.post.assert_called_with('https://api.netatmo.net/api/setthermpoint',
                                            data=dict(device_id=device_id, module_id=module_id,
                                                      setpoint_mode=setpoint_mode, setpoint_endtime=setpoint_endtime,
                                                      setpoint_temp=setpoint_temp),
                                            json=None)

    def test_switch_schedule(self):
        device_id = 'test-device-id'
        module_id = 'test-module-id'
        schedule_id = 'test-schedule-id'

        self.client.post.return_value = mock_response('https://api.netatmo.net/api/switchschedule',
                                                      httplib.OK,
                                                      None,
                                                      'api', 'switchschedule', 'POST.json')

        self.client.energy.switch_schedule(device_id=device_id,
                                           module_id=module_id,
                                           schedule_id=schedule_id)

        self.client.post.assert_called_with('https://api.netatmo.net/api/switchschedule',
                                            data=dict(device_id=device_id, module_id=module_id,schedule_id=schedule_id),
                                            json=None)

    def test_sync_schedule(self):
        device_id = 'test-device-id'
        module_id = 'test-module-id'

        self.client.post.return_value = mock_response('https://api.netatmo.net/api/syncschedule',
                                                      httplib.OK,
                                                      None,
                                                      'api', 'syncschedule', 'POST.json')

        self.client.energy.sync_schedule(device_id=device_id,
                                         module_id=module_id,
                                         zones=[],
                                         timetable=[])
        self.client.post.assert_called_with('https://api.netatmo.net/api/syncschedule',
                                            data=dict(device_id=device_id, module_id=module_id,
                                                      zones='[]', timetable='[]'),
                                            json=None)
