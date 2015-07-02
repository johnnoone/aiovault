from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_lookup_1(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    token = yield from client.auth.lookup_self()
    assert token.id == dev_server.root_token


@async_test
def test_lookup_2(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    token = yield from client.auth.lookup(dev_server.root_token)
    assert token.id == dev_server.root_token


@async_test
def test_lookup_3(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    token1 = yield from client.auth.create()
    token2 = yield from client.auth.lookup(token1.id)
    assert token2.id == token1.id


@async_test
def test_renew(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    token = yield from client.auth.create(lease='1h')
    token = yield from client.auth.renew(token)


@async_test
def test_revoke_prefix(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    token = yield from client.auth.create()
    yield from client.auth.lookup(token)
    revoked = yield from client.auth.revoke_prefix('auth/token/')
    assert revoked is True

    with pytest.raises(KeyError):
        yield from client.auth.lookup(token)


@async_test
def test_revoke_cascade(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    parent_token = yield from client.auth.create()

    client_b = Vault(dev_server.addr, token=parent_token)
    child_token = yield from client_b.auth.create()

    yield from client.auth.lookup(parent_token)
    yield from client.auth.lookup(child_token)

    yield from client.auth.revoke(parent_token)
    with pytest.raises(KeyError):
        yield from client.auth.lookup(parent_token)
    with pytest.raises(KeyError):
        yield from client.auth.lookup(child_token)


@async_test
def test_revoke_orphan(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    parent_token = yield from client.auth.create()

    client_b = Vault(dev_server.addr, token=parent_token)
    child_token = yield from client_b.auth.create()

    yield from client.auth.lookup(parent_token)
    yield from client.auth.lookup(child_token)

    yield from client.auth.revoke_orphan(parent_token)
    with pytest.raises(KeyError):
        yield from client.auth.lookup(parent_token)
    yield from client.auth.lookup(child_token)
