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
    response = yield from client.req_handler('POST',
                                             '/auth/userpass/login/mitchellh',
                                             json={"password": "foo"})
    result = yield from response.json()
    assert result['auth']['metadata'] == {'username': 'mitchellh'}

    # nicer login
    result = yield from client.auth.login('userpass', 'mitchellh', password='foo')
    assert result['auth']['metadata'] == {'username': 'mitchellh'}


@async_test
def test_github(dev_server):
    client = Vault(dev_server['addr'],
                   token=dev_server['root_token'])

    response = yield from client.req_handler('GET', '/sys/auth/github/login',
                                             params={"help": 1})
    data = yield from response.json()
    print(data['help'])

    # low level create/delete

    response = yield from client.req_handler('POST', '/sys/auth/github',
                                             json={"type": "github"})
    assert response.status == 204, 'Must add github auth backend'
    response = yield from client.req_handler('DELETE', '/sys/auth/github')
    assert response.status == 204, 'Must delete github auth backend'

    # high level create/delete

    response = yield from client.auth.add('github')
    assert response is True, 'Must add github auth backend'
    response = yield from client.auth.delete('github')
    assert response is True, 'Must delete github auth backend'


@async_test
def test_doc(dev_server):
    client = Vault(dev_server['addr'],
                   token=dev_server['root_token'])

    response = yield from client.req_handler('GET', '/sys/auth/github',
                                             params={"help": 1})
    data = yield from response.json()
