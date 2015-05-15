from aiovault import Vault, LoginError
from conftest import async_test
import pytest


@async_test
def test_github_loading(dev_server):
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


@async_test
def test_github_loading(dev_server):
    client = Vault(dev_server['addr'],
                   token=dev_server['root_token'])
    added = yield from client.auth.add('github')
    assert added

    store = yield from client.auth.load('github')
    configured = yield from store.configure_organization('tasty-chicks')
    assert configured

    configured = yield from store.configure_team('test', policies='foo')
    assert configured


    client2 = Vault(dev_server['addr'])
    github_token='1111111111111111111111111111111111111111'
    with pytest.raises(LoginError):
        yield from client2.auth.login('github',
                                      github_token=github_token)
    github_token='7208a'+'181a5d54691a42607ac863'+'e3308f3b052cb'
    token = yield from client2.auth.login('github',
                                          github_token=github_token)
