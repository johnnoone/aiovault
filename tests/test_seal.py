from aiovault import Vault
from conftest import async_test


@async_test
def test_initial_status(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    response = yield from client.seal.status()
    assert response.sealed == dev_server.sealed
    assert response.threshold == dev_server.threshold
    assert response.shares == dev_server.shares
    assert response.progress == dev_server.progress


@async_test
def test_seal(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    status = yield from client.seal.status()
    assert status.sealed is False

    sealed = yield from client.seal.seal()
    assert sealed is True

    status = yield from client.seal.status()
    assert status.sealed is True

    status = yield from client.seal.unseal(dev_server.shares,
                                           dev_server.unseal_key)
    assert status.sealed is False
