import httplib
import unittest

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestSecurity(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get_events_until(self):
        home_id = 'test-home-id'
        event_id = 'test-event-id'

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/geteventsuntil',
                                          httplib.OK,
                                          None,
                                          'api', 'geteventsuntil', 'GET.json')

        result = self.client.security.get_events_until(home_id=home_id, event_id=event_id)

        self.client.get.assert_called_with('https://api.netatmo.net/api/geteventsuntil',
                                           params=dict(home_id=home_id, event_id=event_id))
        self.assertEqual(len(result['events_list']), 4)

    def test_get_next_events(self):
        home_id = 'test-home-id'
        event_id = 'test-event-id'
        size = 10

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getnextevents',
                                          httplib.OK,
                                          None,
                                          'api', 'getnextevents', 'GET.json')

        result = self.client.security.get_next_events(home_id=home_id, event_id=event_id, number_of_events=size)

        self.client.get.assert_called_with('https://api.netatmo.net/api/getnextevents',
                                           params=dict(home_id=home_id, event_id=event_id, size=size))
        self.assertEqual(len(result['events_list']), 30)

    def test_get_last_event_of(self):
        home_id = 'test-home-id'
        person_id = 'test-person-id'
        size = 10

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getlasteventof',
                                          httplib.OK,
                                          None,
                                          'api', 'getlasteventof', 'GET.json')

        result = self.client.security.get_last_event_of(home_id=home_id, person_id=person_id, number_of_events=size)

        self.client.get.assert_called_with('https://api.netatmo.net/api/getlasteventof',
                                           params=dict(home_id=home_id, person_id=person_id, size=size))
        self.assertEqual(len(result['events_list']), 51)

    def test_add_webhook(self):
        url = 'test-url'

        self.client.post.return_value = mock_response('https://api.netatmo.net/api/addwebhook',
                                           httplib.OK,
                                           None,
                                           'api', 'addwebhook', 'POST.json')

        self.client.security.add_webhook(url=url)

        self.client.post.assert_called_with('https://api.netatmo.net/api/addwebhook',
                                            data=dict(url=url, app_types='app_camera'), json=None)

    def test_drop_webhook(self):
        self.client.post.return_value = mock_response('https://api.netatmo.net/api/dropwebhook',
                                           httplib.OK,
                                           None,
                                           'api', 'dropwebhook', 'POST.json')

        self.client.security.drop_webhook()

        self.client.post.assert_called_with('https://api.netatmo.net/api/dropwebhook',
                                            data=dict(app_types='app_camera'), json=None)

    def test_get_camera_picture(self):
        image_id = 'test-image-id'
        key = 'test-key'

        self.client.get.return_value = mock_response('https://api.netatmo.net/api/getcamerapicture',
                                          httplib.OK,
                                          None,
                                          'api', 'getcamerapicture', 'GET.bin')

        result = self.client.security.get_camera_picture(image_id=image_id, key=key)

        self.client.get.assert_called_with('https://api.netatmo.net/api/getcamerapicture',
                                           params=dict(image_id=image_id, key=key))
        self.assertEqual(len(result), 21638)
