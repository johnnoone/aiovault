from aiovault import Vault
from conftest import async_test


@async_test
def test_auth(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # list mounted backends
    backends = yield from client.auth.items()
    assert len(backends) == 1

    response = yield from client.auth.enable('app-id')
    backends = yield from client.auth.items()
    assert len(backends) == 2
    assert 'app-id' in backends


@async_test
def test_secret(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # list mounted backends
    backends = yield from client.secret.items()
    assert len(backends) == 2

    response = yield from client.secret.mount('consul')
    backends = yield from client.secret.items()
    assert len(backends) == 3
    assert 'consul' in backends

    response = yield from client.secret.move('consul', 'newpath')
    backends = yield from client.secret.items()
    assert len(backends) == 3
    assert 'newpath' in backends

    response = yield from client.secret.unmount('newpath')
    backends = yield from client.secret.items()
    assert len(backends) == 2
