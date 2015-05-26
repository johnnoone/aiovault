from aiovault import Vault
from conftest import async_test


@async_test
def test_renew(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    response = yield from client.write('/secret/foo', json={
        'data': 'bar', 'lease': '1h'
    })
    assert response.status == 204

    response = yield from client.read('/secret/foo')
    result = yield from response.json()
    renewed = yield from client.lease.renew(result['lease_id'])


@async_test
def test_revoke(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    revoked = yield from client.lease.revoke('foo/1234')
    assert revoked


@async_test
def test_revoke_prefix(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    revoked = yield from client.lease.revoke_prefix('foo/1234')
    assert revoked
