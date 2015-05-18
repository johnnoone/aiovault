from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_generic(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    store = yield from client.secret.load('secret')
    assert store.__repr__() == "<GenericBackend(name='secret')>"

    data = yield from store.write('foo', {'value': 'bar'})
    assert data

    data = yield from store.read('foo')
    assert data == {'value': 'bar'}

    data = yield from store.delete('foo')
    assert data

    with pytest.raises(ValueError):
        yield from store.write('bar', 'baz')

    with pytest.raises(KeyError):
        yield from store.read('bar')

    data = yield from store.delete('bar')
    assert data is True

    data = yield from store.delete('bar')
    assert data is True

