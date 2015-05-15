from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_userpass(dev_server):
    client = Vault(dev_server['addr'],
                   token=dev_server['root_token'])

    # enable userpass
    response = yield from client.auth.add('userpass')
    assert response

    auth = yield from client.auth.load('userpass')

    response = yield from auth.create('mitchellh', 'foo')
    assert response

    # raw login
    response = yield from client.write('/auth/userpass/login/mitchellh',
                                       json={"password": "foo"})
    result = yield from response.json()
    assert result['auth']['metadata'] == {'username': 'mitchellh'}

    # nicer login
    result = yield from client.auth.login('userpass', username='mitchellh', password='foo')
    assert result['metadata'] == {'username': 'mitchellh'}
