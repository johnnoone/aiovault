from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_policy(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    policies = yield from client.policy.items()
    assert 'root' in policies
    assert 'foo' not in policies

    absent = yield from client.policy.delete('foo')
    assert absent is True

    absent = yield from client.policy.delete('foo')
    assert absent is True

    policy = yield from client.policy.read('root')
    assert policy.name == 'root'

    with pytest.raises(KeyError):
        yield from client.policy.read('foo')

    rules = {
        'sys': {
            'policy': 'deny'
        }
    }

    written = yield from client.policy.write('foo', rules)
    assert written is True

    policy = yield from client.policy.read('foo')
    assert policy.name == 'foo'
    assert 'sys' in policy
    assert policy.rules == rules
    assert policy == rules

    # add other rules
    policy['bar/baz'] = 'deny'

    written = yield from client.policy.write('foo', policy)
    assert written is True

    policy = yield from client.policy.read('foo')
    assert policy.name == 'foo'
    assert 'sys' in policy
    assert 'bar/baz' in policy


@async_test
def test_policy_hl(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    policies = yield from client.policy.items()
    assert 'root' in policies

    response = yield from client.policy.write_path('foo', 'my/path', 'read')
    assert response
    rules = yield from client.policy.read('foo')
    assert 'my/path' in rules
    assert 'cert' not in rules

    backend = client.auth.load('cert')
    response = yield from client.policy.write_path('foo', backend, 'read')
    assert response
    rules = yield from client.policy.read('foo')
    assert 'my/path' in rules
    assert 'auth/cert' in rules

    response = yield from client.policy.delete_path('foo', 'my/path')
    assert response
    rules = yield from client.policy.read('foo')
    assert 'my/path' not in rules
    assert 'auth/cert' in rules
