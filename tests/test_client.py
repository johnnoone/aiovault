from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_github(dev_server):
    client = Vault(dev_server['addr'],
                   token=dev_server['root_token'])

    response = yield from client.read('/sys/auth/github/login',
                                      params={"help": 1})
    data = yield from response.json()
    print(data['help'])

    # low level create/delete

    response = yield from client.write('/sys/auth/github',
                                       json={"type": "github"})
    assert response.status == 204, 'Must add github auth backend'
    response = yield from client.delete('/sys/auth/github')
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

    response = yield from client.read('/sys/auth/github',
                                      params={"help": 1})
    data = yield from response.json()
