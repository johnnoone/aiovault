import pytest
from aiovault import MountError, Vault
from conftest import async_test


@async_test
def test_auth(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # list mounted backends
    backends = yield from client.auth.items()
    assert len(backends) == 1

    yield from client.auth.enable('app-id')
    backends = yield from client.auth.items()
    assert len(backends) == 2
    assert 'app-id' in backends


@async_test
def test_secret(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # list mounted backends
    backends = yield from client.secret.items()
    assert len(backends) == 2

    yield from client.secret.mount('consul')
    backends = yield from client.secret.items()
    assert len(backends) == 3
    assert 'consul' in backends

    yield from client.secret.remount('consul', 'newpath')
    backends = yield from client.secret.items()
    assert len(backends) == 3
    assert 'newpath' in backends

    yield from client.secret.unmount('newpath')
    backends = yield from client.secret.items()
    assert len(backends) == 2


@async_test
def test_secret_2(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # list mounted backends
    backends = yield from client.secret.items()
    assert len(backends) == 2

    mounted, backend = yield from client.secret.mount('consul')
    backends = yield from client.secret.items()
    assert len(backends) == 3
    assert 'consul' in backends

    yield from backend.remount('newpath')
    backends = yield from client.secret.items()
    assert len(backends) == 3
    assert 'newpath' in backends

    yield from backend.unmount()
    backends = yield from client.secret.items()
    assert len(backends) == 2


@async_test
def test_secret_mount(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('consul')
    assert mounted is True, 'must be mounted'

    mounted, _ = yield from client.secret.mount('consul')
    assert mounted is False, 'must be already mounted'

    with pytest.raises(MountError):
        # already mounted
        yield from backend.mount()

    yield from backend.unmount()

    unmounted = yield from client.secret.unmount('consul')
    assert unmounted is False, 'must be already unmounted'

    with pytest.raises(MountError):
        # already unmounted
        yield from backend.unmount()
