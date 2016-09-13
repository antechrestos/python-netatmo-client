import httplib
import json
import logging
import os
import urllib

import requests

_logger = logging.getLogger(__name__)


class InvalidStatusCode(Exception):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def __str__(self):
        if self.body is None:
            return '%d' % self.status_code
        elif type(self.body) == str:
            return '%d : %s' % (self.status_code, self.body)
        else:
            return '%d : %s' % (self.status_code, json.dumps(self.body))


class NoTokenProvided(Exception):
    pass


class Domain(object):
    def __init__(self, api_caller):
        self._api_caller = api_caller


class Station(Domain):
    def get_station_data(self, device_id=None, get_favorites=False):
        params = dict()
        if device_id is not None:
            params['device_id'] = device_id
        if get_favorites:
            params['get_favorites'] = True
        return self._api_caller(requests.get, '/getstationsdata', params=params)


class Thermostat(Domain):
    def get_thermostat_data(self, device_id=None):
        params = dict()
        if device_id is not None:
            params['device_id'] = device_id
        return self._api_caller(requests.get, '/getthermostatsdata', params=params)

    def create_new_schedule(self, device_id, module_id, name, zones, timetable):
        form = dict(device_id=device_id, module_id=module_id, name=name, zones=zones, timetable=timetable)
        return self._api_caller(requests.post, '/createnewschedule', data=form)

    def set_therm_point(self, device_id, module_id, setpoint_mode, setpoint_endtime=None, setpoint_temp=None):
        form = dict(device_id=device_id, module_id=module_id, setpoint_mode=setpoint_mode)
        if setpoint_endtime is not None:
            form['setpoint_endtime'] = setpoint_endtime
        if setpoint_temp is not None:
            form['setpoint_temp'] = setpoint_temp
        self._api_caller(requests.post, '/setthermpoint', data=form)

    def switch_schedule(self, device_id, module_id, schedule_id):
        form = dict(device_id=device_id, module_id=module_id, schedule_id=schedule_id)
        self._api_caller(requests.post, '/switchschedule', data=form)

    def sync_schedule(self, device_id, module_id, zones, timetable):
        form = dict(device_id=device_id, module_id=module_id, zones=zones, timetable=timetable)
        self._api_caller(requests.post, '/syncschedule', data=form)


class Camera(Domain):
    def get_home_data(self, home_id=None, number_of_events=None):
        params = dict()
        if home_id is not None:
            params['home_id'] = home_id
        if number_of_events is not None:
            params['size'] = number_of_events
        return self._api_caller(requests.get, '/gethomedata', params=params)

    def get_camera_picture(self, image_id, key):
        params = dict(image_id=image_id, key=key)
        return self._api_caller(requests.get, '/getcamerapicture', params=params)

    def get_events_until(self, home_id, event_id):
        params = dict(home_id=home_id, event_id=event_id)
        return self._api_caller(requests.get, '/geteventsuntil', params=params)

    def get_next_events(self, home_id, event_id, size=None):
        params = dict(home_id=home_id, event_id=event_id)
        if size is not None:
            params['size'] = size
        return self._api_caller(requests.get, '/getnextevents', params=params)

    def get_last_event_of(self, home_id, person_id, size=None):
        params = dict(home_id=home_id, person_id=person_id)
        if size is not None:
            params['size'] = size
        return self._api_caller(requests.get, '/getlasteventof', params=params)

    def add_webhook(self, url):
        data = dict(url=url, app_types='app_camera')
        self._api_caller(requests.post, '/addwebhook', data=data)

    def drop_webhook(self):
        data = dict(app_types='app_camera')
        self._api_caller(requests.post, '/dropwebhook', data=data)

    def ping(self, home_id, camera_id):
        home = self.get_home_data(home_id, 0)
        for camera in home['cameras']:
            if camera['id'] == camera_id:
                if camera['status'] != 'on':
                    return False
                if not camera.get('is_local', False):
                    return False
                try:
                    response = NetatmoClient.check_status_code(
                        requests.get('%s/command/ping' % camera['vpn_url'])
                    )
                    response_locale = NetatmoClient.check_status_code(
                        requests.get('%s/command/ping' % response['local_url'])
                    )
                    return response_locale['local_url'] == response['local_url']
                except InvalidStatusCode:
                    return False
        return False


class NetatmoClient(object):
    AUTHORIZED_URL = 'https://api.netatmo.com/oauth2/authorize'

    TOKEN_URL = 'https://api.netatmo.com/oauth2/token'

    API_BASE_URL = 'https://api.netatmo.net/api'

    INVALID_ACCESS_TOKEN = 2

    ACCESS_TOKEN_EXPIRED = 3

    PROXY = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._refresh_token = None
        self._station = Station(self._call_api)
        self._thermostat = Thermostat(self._call_api)
        self._camera = Camera(self._call_api)

    def generate_auth_url(self, redirect_uri, state, *scopes):
        parameters = dict(client_id=self.client_id,
                          redirect_uri=redirect_uri,
                          scope=' '.join(scopes),
                          state=state)
        return '%s?%s' % (NetatmoClient.AUTHORIZED_URL,
                          '&'.join('%s=%s' % (k, urllib.quote(v, safe='~()*!.\'')) for k, v in parameters.items()))

    def request_token_with_code(self, code, redirect_uri, *scopes):
        form = dict(client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=redirect_uri,
                    scope=' '.join(scopes),
                    code=code,
                    grant_type='authorization_code')
        self._request_tokens(form)

    def request_token_with_client_credentials(self, username, password, *scopes):
        form = dict(client_id=self.client_id,
                    client_secret=self.client_secret,
                    username=username,
                    password=password,
                    scope=' '.join(scopes),
                    grant_type='password')
        self._request_tokens(form)

    def request_refresh_token(self, refresh_token=None):
        form = dict(client_id=self.client_id,
                    client_secret=self.client_secret,
                    refresh_token=refresh_token if refresh_token is not None else self._refresh_token,
                    grant_type='refresh_token')
        self._request_tokens(form)

    @property
    def station(self):
        self._check_token()
        return self._station

    @property
    def thermostat(self):
        self._check_token()
        return self._thermostat

    @property
    def camera(self):
        self._check_token()
        return self._camera

    def _check_token(self):
        if self._access_token is None or self._refresh_token is None:
            raise NoTokenProvided()

    def _call_api(self, method, uri, **kwargs):
        def _set_token_in_request():
            if 'params' in kwargs:
                kwargs['params']['access_token'] = self._access_token
            elif 'data' in kwargs:
                kwargs['data']['access_token'] = self._access_token
            else:
                kwargs['params'] = dict(access_token=self._access_token)

        _set_token_in_request()
        try:
            response = NetatmoClient._invoke(method,
                                             '%s%s' % (NetatmoClient.API_BASE_URL, uri),
                                             **kwargs) \
                .json()
        except InvalidStatusCode, i:
            if NetatmoClient._is_token_expired(i):
                try:
                    self.request_refresh_token()
                    _set_token_in_request()
                    response = NetatmoClient._invoke(method,
                                                     '%s%s' % (NetatmoClient.API_BASE_URL, uri),
                                                     **kwargs) \
                        .json()
                except InvalidStatusCode, other:
                    if other.status_code / 100 == 4:
                        self._access_token = None
                        self._refresh_token = None
                    raise
            else:
                raise
        _logger.debug('%s - %s', uri, json.dumps(response))
        if response['status'] != "ok":
            raise InvalidStatusCode(httplib.INTERNAL_SERVER_ERROR, response)
        else:
            return response.get('body')

    def _request_tokens(self, form):
        response = NetatmoClient._invoke(requests.post, NetatmoClient.TOKEN_URL, data=form)
        tokens = response.json()
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']

    @staticmethod
    def _is_token_expired(i):
        if i.status_code == httplib.FORBIDDEN and type(i.body) == dict and i.body.get('error') is not None:
            code = i.body['error'].get('code')
            return code == NetatmoClient.INVALID_ACCESS_TOKEN or code == NetatmoClient.ACCESS_TOKEN_EXPIRED
        else:
            return False

    @staticmethod
    def _invoke(invocation, url, **kwargs):
        logging.debug('%s - %s', invocation.__name__, kwargs.get('data'))
        kwargs['verify'] = False
        kwargs['proxies'] = NetatmoClient.PROXY
        response = invocation(url, **kwargs)
        return NetatmoClient.check_status_code(response)

    @staticmethod
    def check_status_code(response):
        if response.status_code / 100 == 2:
            return response
        else:
            try:
                body = response.json()
            except Exception, _:
                body = response.text
            raise InvalidStatusCode(response.status_code, body)
