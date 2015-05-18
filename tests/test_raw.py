from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_raw(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    with pytest.raises(KeyError):
        yield from client.raw.read('foo')

    writed = yield from client.raw.write('foo', {'bar': 'baz'})

    response = yield from client.raw.read('foo')
    print(response)
    assert response['value'] == {'bar': 'baz'}

    response = yield from client.raw.delete('foo')
    assert response is True

    # still absent
    response = yield from client.raw.delete('foo')
    assert response is True
