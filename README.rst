Netatmo python client
=====================
.. image:: https://img.shields.io/pypi/v/netatmo-client.svg
    :target: https://pypi.python.org/pypi/netatmo-client
.. image:: https://img.shields.io/github/license/antechrestos/python-netatmo-client.svg
	:target: https://raw.githubusercontent.com/antechrestos/python-netatmo-client/master/LICENSE

The python-netatmo-client repo contains a Python client library for Netatmo.

Installing
==========
So far only source is the way of installing it:

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
    client = NetatmoClient(client_id, client_secret)

Get the tokens
--------------

The library provides you two way of logging the client

Grant code process
~~~~~~~~~~~~~~~~~~

Providing that you declared ``http://somewhere.org/callback/grant/code`` as a **redirect uri** on the netatmo site,
you may generate your *grant code* url.

.. code-block:: python

    client.generate_auth_url('http://somewhere.org/callback/grant/code', 'state-generated', *scopes)

The user will be lead to the grant code process and return to your site with
a url such as ``http://somewhere.org/callback/grant/code?code=<your code>&state=state-generated``

Then all you have to do is **exchange** the code with a couple of *access token* and *refresh token*:

.. code-block:: python

    client.request_token_with_code('your code', 'http://somewhere.org/callback/grant/code', *scopes)

Client credentials
~~~~~~~~~~~~~~~~~~

You may also choose this process as follows:

.. code-block:: python

    client.request_token_with_client_credentials('username', 'password', *scopes)

The api calls
-------------

The client defines three parts:

- ``common``:
    - ``get_measure``
- ``station``:
    - ``get_station_data``
- ``thermostat``:
    - ``get_thermostat_data``
    - ``create_new_schedule``
    - ``set_therm_point``
    - ``switch_schedule``
    - ``sync_schedule``
- ``camera``
    - ``get_camera_picture``
    - ``get_events_until``
    - ``get_next_events``
    - ``get_home_data``
    - ``get_last_event_of``
    - ``add_webhook``
    - ``drop_webhook``
    - ``ping``


Issues and contributions
========================
Please submit issue/pull request.
