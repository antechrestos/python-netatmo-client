import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestCamera(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    @mock.patch('netatmo_client.client.requests')
    def test_get_home_data(self, fake_requests):
        fake_requests.get = mock_response('https://api.netatmo.net/api/gethomedata',
                                          'get',
                                          None,
                                          httplib.OK,
                                          None,
                                          'api', 'gethomedata', 'GET.json')
        result = self.client.camera.get_home_data()
        self.assertEqual(result['user']['country'], 'FR')
        self.assertEqual(len(result['homes']), 1)

    @mock.patch('netatmo_client.client.requests')
    def test_get_home_data_by_device(self, fake_requests):
        home_id = 'test-home-id'

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('home_id'), home_id)

        fake_requests.get = mock_response('https://api.netatmo.net/api/gethomedata',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'gethomedata', 'GET_{id}.json')

        result = self.client.camera.get_home_data(home_id=home_id)
        self.assertEqual(result['user']['country'], 'FR')
        self.assertEqual(len(result['homes']), 1)

    @mock.patch('netatmo_client.client.requests')
    def test_get_events_until(self, fake_requests):
        home_id = 'test-home-id'
        event_id = 'test-event-id'

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('home_id'), home_id)
            self.assertEqual(kwargs.get('params').get('event_id'), event_id)

        fake_requests.get = mock_response('https://api.netatmo.net/api/geteventsuntil',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'geteventsuntil', 'GET.json')

        result = self.client.camera.get_events_until(home_id=home_id, event_id=event_id)
        self.assertEqual(len(result['events_list']), 4)

    @mock.patch('netatmo_client.client.requests')
    def test_get_next_events(self, fake_requests):
        home_id = 'test-home-id'
        event_id = 'test-event-id'
        size = 10

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('home_id'), home_id)
            self.assertEqual(kwargs.get('params').get('event_id'), event_id)
            self.assertEqual(kwargs.get('params').get('size'), size)

        fake_requests.get = mock_response('https://api.netatmo.net/api/getnextevents',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'getnextevents', 'GET.json')

        result = self.client.camera.get_next_events(home_id=home_id, event_id=event_id, size=size)
        self.assertEqual(len(result['events_list']), 30)

    @mock.patch('netatmo_client.client.requests')
    def test_get_last_event_of(self, fake_requests):
        home_id = 'test-home-id'
        person_id = 'test-person-id'
        size = 10

        def _check_data(**kwargs):
            self.assertIsNotNone(kwargs.get('params'))
            self.assertEqual(kwargs.get('params').get('home_id'), home_id)
            self.assertEqual(kwargs.get('params').get('person_id'), person_id)
            self.assertEqual(kwargs.get('params').get('size'), size)

        fake_requests.get = mock_response('https://api.netatmo.net/api/getlasteventof',
                                          'get',
                                          _check_data,
                                          httplib.OK,
                                          None,
                                          'api', 'getlasteventof', 'GET.json')

        result = self.client.camera.get_last_event_of(home_id=home_id, person_id=person_id, size=size)
        self.assertEqual(len(result['events_list']), 51)

    @mock.patch('netatmo_client.client.requests')
    def test_add_webhook(self, fake_requests):
        url = 'test-url'

        def _check_form(**kwargs):
            self.assertIsNotNone(kwargs.get('data'))
            form = kwargs.get('data')
            self.assertEqual(form.get('url'), url)
            self.assertEqual(form.get('app_types'), 'app_camera')

        fake_requests.post = mock_response('https://api.netatmo.net/api/addwebhook',
                                           'post',
                                           _check_form,
                                           httplib.OK,
                                           None,
                                           'api', 'addwebhook', 'POST.json')

        self.client.camera.add_webhook(url=url)

    @mock.patch('netatmo_client.client.requests')
    def test_drop_webhook(self, fake_requests):
        def _check_form(**kwargs):
            self.assertIsNotNone(kwargs.get('data'))
            form = kwargs.get('data')
            self.assertEqual(form.get('app_types'), 'app_camera')

        fake_requests.post = mock_response('https://api.netatmo.net/api/dropwebhook',
                                           'post',
                                           _check_form,
                                           httplib.OK,
                                           None,
                                           'api', 'dropwebhook', 'POST.json')

        self.client.camera.drop_webhook()
