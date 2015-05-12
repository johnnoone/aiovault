from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_status(dev_server):
    client = Vault(dev_server['addr'],
                   token=dev_server['root_token'])

    response = yield from client.status()
    assert response.initialized is True

    response = yield from client.leader()
    assert response.enabled is False
    assert response.is_self is False

    response = yield from client.health()
    assert response.initialized is True
    assert response.sealed is dev_server['sealed']
