from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_lookup_1(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    token = yield from backend.lookup_self()
    assert token.id == dev_server.root_token


@async_test
def test_lookup_2(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    token = yield from backend.lookup(dev_server.root_token)
    assert token.id == dev_server.root_token


@async_test
def test_lookup_3(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    token1 = yield from backend.create()
    token2 = yield from backend.lookup(token1.id)
    assert token2.id == token1.id


@async_test
def test_renew(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    token = yield from backend.create(lease='1h')
    token = yield from backend.renew(token)


@async_test
def test_revoke_prefix(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    token = yield from backend.create()
    yield from backend.lookup(token)
    revoked = yield from backend.revoke_prefix('auth/token/')
    assert revoked is True

    with pytest.raises(KeyError):
        yield from backend.lookup(token)


@async_test
def test_revoke_cascade(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    parent_token = yield from backend.create()

    client_b = Vault(dev_server.addr, token=parent_token)
    backend_b = yield from client_b.auth.get('token')
    child_token = yield from backend_b.create()

    yield from backend.lookup(parent_token)
    yield from backend.lookup(child_token)

    yield from backend.revoke(parent_token)
    with pytest.raises(KeyError):
        yield from backend.lookup(parent_token)
    with pytest.raises(KeyError):
        yield from backend.lookup(child_token)


@async_test
def test_revoke_orphan(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.get('token')
    parent_token = yield from backend.create()

    client_b = Vault(dev_server.addr, token=parent_token)
    backend_b = yield from client_b.auth.get('token')
    child_token = yield from backend_b.create()

    yield from backend.lookup(parent_token)
    yield from backend.lookup(child_token)

    yield from backend.revoke_orphan(parent_token)
    with pytest.raises(KeyError):
        yield from backend.lookup(parent_token)
    yield from backend.lookup(child_token)
