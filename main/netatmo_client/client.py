import httplib
import json
import logging
import os

import requests
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation

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

    @staticmethod
    def _set_optional(form, parameter_name, parameter_value):
        if parameter_value is not None:
            form[parameter_name] = parameter_value

    @staticmethod
    def _set_json_parameter(form, parameter_name, parameter_value):
        if parameter_value is not None:
            form[parameter_name] = json.dumps(parameter_value, separators=(',', ':'))


class Common(Domain):
    def get_measure(self, device_id, module_id, scale, measure_types, date_begin=None, date_end=None,
                    limit=None, optimize=None, real_time=None):
        params = dict(device_id=device_id, module_id=module_id, scale=scale, type=','.join(measure_types))
        Domain._set_optional(params, 'date_begin', date_begin)
        Domain._set_optional(params, 'date_end', date_end)
        Domain._set_optional(params, 'limit', limit)
        Domain._set_optional(params, 'optimize', optimize)
        Domain._set_optional(params, 'real_time', real_time)
        return self._api_caller._get('/getmeasure', params=params)


class Public(Domain):
    def get_public_data(self, lat_ne, lon_ne, lat_sw, lon_sw, required_measure_types=None, filter_abnormal=None):
        params = dict(lat_ne=lat_ne, lon_ne=lon_ne, lat_sw=lat_sw, lon_sw=lon_sw)
        Domain._set_optional(params, 'required_data',
                             None if required_measure_types is None else ','.join(required_measure_types))
        Domain._set_optional(params, 'filter', filter_abnormal)
        return self._api_caller._get('/getpublicdata', params=params)


class Weather(Domain):
    def get_station_data(self, device_id=None, get_favorites=False):
        params = dict()
        Domain._set_optional(params, 'device_id', device_id)
        Domain._set_optional(params, 'get_favorites', get_favorites if get_favorites else None)
        return self._api_caller._get('/getstationsdata', params=params)


class Energy(Domain):
    def get_home_data(self, home_id=None, *gateway_types):
        params = dict()
        Domain._set_optional(params, 'home_id', home_id)
        Domain._set_optional(params, 'gateway_type', None if len(gateway_types) == 0 else ','.join(gateway_types))
        return self._api_caller._get('/homesdata', params=params)

    def get_thermostat_data(self, device_id=None):
        params = dict()
        Domain._set_optional(params, 'device_id', device_id)
        return self._api_caller._get('/getthermostatsdata', params=params)

    def create_new_schedule(self, device_id, module_id, name, zones, timetable):
        form = dict(device_id=device_id,
                    module_id=module_id,
                    name=name)
        Domain._set_json_parameter(form, 'zones', zones)
        Domain._set_json_parameter(form, 'timetable', timetable)
        return self._api_caller._post('/createnewschedule', data=form)

    def set_therm_point(self, device_id, module_id, setpoint_mode, setpoint_endtime=None, setpoint_temp=None):
        form = dict(device_id=device_id, module_id=module_id, setpoint_mode=setpoint_mode)
        Domain._set_optional(form, 'setpoint_endtime', setpoint_endtime)
        Domain._set_optional(form, 'setpoint_temp', setpoint_temp)
        self._api_caller._post('/setthermpoint', data=form)

    def switch_schedule(self, device_id, module_id, schedule_id):
        form = dict(device_id=device_id, module_id=module_id, schedule_id=schedule_id)
        self._api_caller._post('/switchschedule', data=form)

    def sync_schedule(self, device_id, module_id, zones, timetable):
        form = dict(device_id=device_id,
                    module_id=module_id)
        Domain._set_json_parameter(form, 'zones', zones)
        Domain._set_json_parameter(form, 'timetable', timetable)
        self._api_caller._post('/syncschedule', data=form)


class Security(Domain):
    def get_camera_picture(self, image_id, key):
        params = dict(image_id=image_id, key=key)
        return self._api_caller.check_status_code(
            self._api_caller.get('%s/getcamerapicture' % NetatmoClient.API_BASE_URL, params=params)
        ).content

    def get_events_until(self, home_id, event_id):
        params = dict(home_id=home_id, event_id=event_id)
        return self._api_caller._get('/geteventsuntil', params=params)

    def get_next_events(self, home_id, event_id, number_of_events=None):
        params = dict(home_id=home_id, event_id=event_id)
        Domain._set_optional(params, 'size', number_of_events)
        return self._api_caller._get('/getnextevents', params=params)

    def get_last_event_of(self, home_id, person_id, number_of_events=None):
        params = dict(home_id=home_id, person_id=person_id)
        Domain._set_optional(params, 'size', number_of_events)
        return self._api_caller._get('/getlasteventof', params=params)

    def add_webhook(self, url):
        data = dict(url=url, app_types='app_camera')
        self._api_caller._post('/addwebhook', data=data)

    def drop_webhook(self):
        data = dict(app_types='app_camera')
        self._api_caller._post('/dropwebhook', data=data)

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


class NetatmoClient(CredentialManager):
    AUTHORIZED_URL = 'https://api.netatmo.com/oauth2/authorize'

    TOKEN_URL = 'https://api.netatmo.com/oauth2/token'

    API_BASE_URL = 'https://api.netatmo.net/api'

    INVALID_ACCESS_TOKEN = 2

    ACCESS_TOKEN_EXPIRED = 3

    PROXY = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))

    def __init__(self, client_id, client_secret, scopes):
        super(NetatmoClient, self).__init__(ServiceInformation(self.AUTHORIZED_URL,
                                                               self.TOKEN_URL,
                                                               client_id, client_secret,
                                                               scopes),
                                            self.PROXY)
        self._common = Common(self)
        self._public = Public(self)
        self._weather = Weather(self)
        self._energy = Energy(self)
        self._security = Security(self)
        self._access_token_value = None

    def _grant_code_request(self, code, redirect_uri):
        result = super(NetatmoClient, self)._grant_code_request(code, redirect_uri)
        result['client_id'] = self.service_information.client_id
        result['client_secret'] = self.service_information.client_secret
        return result

    def _grant_password_request(self, login, password):
        result = super(NetatmoClient, self)._grant_password_request(login, password)
        result['client_id'] = self.service_information.client_id
        result['client_secret'] = self.service_information.client_secret
        return result

    def _grant_refresh_token_request(self, refresh_token):
        result = super(NetatmoClient, self)._grant_refresh_token_request(refresh_token)
        result.pop('scope')
        result['client_id'] = self.service_information.client_id
        result['client_secret'] = self.service_information.client_secret
        return result

    def _token_request(self, request_parameters, refresh_token_mandatory):
        response = requests.post(NetatmoClient.TOKEN_URL, data=request_parameters)
        if response.status_code != 200:
            CredentialManager._handle_bad_response(response)
        else:
            self._process_token_response(response.json(), refresh_token_mandatory)

    @property
    def _access_token(self):
        return self._access_token_value

    @_access_token.setter
    def _access_token(self, access_token):
        if self._session is None:
            self._session = requests.Session()
            self._session.proxies = self.proxies
            self._session.verify = self.service_information.verify
            self._session.trust_env = False
        self._access_token_value = access_token

    def _bearer_request(self, method, url, **kwargs):
        headers = kwargs.get('headers')
        if headers is None:
            headers = dict()
            kwargs['headers'] = headers
        if 'params' in kwargs:
            kwargs['params']['access_token'] = self._access_token
        elif 'data' in kwargs:
            kwargs['data']['access_token'] = self._access_token
        else:
            kwargs['params'] = dict(access_token=self._access_token)
        _logger.debug("_bearer_request on %s - %s" % (method.__name__, url))
        response = method(url, **kwargs)
        if self.refresh_token is not None and self._is_token_expired(response):
            self._refresh_token()
            return method(url, **kwargs)
        else:
            return response

    @property
    def common(self):
        return self._common

    @property
    def public(self):
        return self._public

    @property
    def weather(self):
        return self._weather

    @property
    def energy(self):
        return self._energy

    @property
    def security(self):
        return self._security

    @staticmethod
    def _is_token_expired(response):
        if response.status_code == httplib.FORBIDDEN :
            try:
                body = response.json()
                code = body.get('error', dict()).get('code')
                return code == NetatmoClient.INVALID_ACCESS_TOKEN or code == NetatmoClient.ACCESS_TOKEN_EXPIRED
            except Exception:
                return False
        else:
            return False

    def _get(self, url, params=None, **kwargs):
        return self.check_status_code(
            self.get('%s%s' % (NetatmoClient.API_BASE_URL, url), params=params, **kwargs)
        ).json().get('body')

    def _post(self, url, data=None, json=None, **kwargs):
        return self.check_status_code(
            self.post('%s%s' % (NetatmoClient.API_BASE_URL, url), data=data, json=json, **kwargs)
        ).json().get('body')

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
