Netatmo python client
=====================
.. image:: https://img.shields.io/pypi/v/netatmo-client.svg
    :target: https://pypi.python.org/pypi/netatmo-client
.. image:: https://img.shields.io/github/license/antechrestos/python-netatmo-client.svg
	:target: https://raw.githubusercontent.com/antechrestos/python-netatmo-client/master/LICENSE

The python-netatmo-client repo contains a Python client library for Netatmo.

Installing
==========

From pip
------------

.. code-block:: bash

	$ pip install netatmo-client

From sources
------------

To build the library run :

.. code-block:: bash

	$ python setup.py install



How to use it
=============
First of all you must declare your **own** application and get your *client id* and *client secret*.

Build an instance
-----------------
.. code-block:: python

    from netatmo_client.client import NetatmoClient
    scopes = ('read_station',
              'read_thermostat',
              'write_thermostat',
              'read_camera')
    client_id = 'client id'
    client_secret = 'client secret'
    client = NetatmoClient(client_id, client_secret, scopes)

Get the tokens
--------------

The library provides you two way of logging the client

Grant code process
~~~~~~~~~~~~~~~~~~

Providing that you declared ``http://somewhere.org/callback/grant/code`` as a **redirect uri** on the netatmo site,
you may get your tokens using the grant code way with a code like follows.

.. code-block:: python

    client = NetatmoClient('client-id', 'client-secret', ['read_station',
              'read_thermostat',
              'write_thermostat',
              'read_camera'])
    redirect_uri = 'http://somewhere.org/callback/grant/code'
    grant_url = client.generate_authorize_url(redirect_uri, 'state-test')
    sys.stdout\
        .write("Open the following url ( %s ), follow the steps and enter the code you will see in the navigation bar: "
               % grant_url)
    code = sys.stdin.readline()
    code = code.rstrip('\r\n')
    client.init_with_authorize_code(redirect_uri, code)
    # use the api
    print json.dumps(client.weather.get_station_data())

The user will be lead to the grant code process and return to your site with
a url such as ``http://somewhere.org/callback/grant/code?code=<your code>&state=state-test``.
Then normally a webserver of yours handles the `GET` request, and exchanges the code using the same **redirect uri** as above.

Client credentials
~~~~~~~~~~~~~~~~~~

You may also choose this process as follows:

.. code-block:: python

    client = NetatmoClient('client-id', 'client-secret', [
                                                            'read_station',
                                                            'read_thermostat',
                                                            'write_thermostat',
                                                            'read_camera'])
    client.init_with_user_credentials('username', 'password')
    # use the api
    print json.dumps(client.energy.get_home_data(None, 'NaPlug', 'NaCamera'))

The api calls
-------------

The client defines several parts:

- ``common``:
    - ``get_measure``
- ``public``:
    - ``get_public_data``
- ``weather``:
    - ``get_station_data``
- ``energy``:
    - ``get_home_data``
    - ``get_thermostat_data``
    - ``create_new_schedule``
    - ``set_therm_point``
    - ``switch_schedule``
    - ``sync_schedule``
- ``security``
    - ``get_camera_picture``
    - ``get_events_until``
    - ``get_next_events``
    - ``get_last_event_of``
    - ``add_webhook``
    - ``drop_webhook``
    - ``ping``


Issues and contributions
========================
Please submit issue/pull request.
