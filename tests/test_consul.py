from aiovault import Vault
from conftest import async_test
import pytest


CONSUL_POLICY = """
key "" {
    policy = "write"
}
"""


@async_test
def test_basic(dev_server, consul):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    added = yield from client.secret.mount('consul')
    assert added

    store = yield from client.secret.get('consul')
    configured = yield from store.config_access(address=consul.address,
                                                token=consul.acl_master_token)
    assert configured

    configured = yield from store.write_role('foo', policy=CONSUL_POLICY)
    assert configured

    data = yield from store.creds('foo')
    assert 'token' in data


@async_test
def test_crud(dev_server, consul):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    added = yield from client.secret.mount('consul')
    assert added

    store = yield from client.secret.get('consul')
    configured = yield from store.config_access(address=consul.address,
                                                token=consul.acl_master_token)
    assert configured

    configured = yield from store.write_role('foo', policy=CONSUL_POLICY)
    assert configured

    role = yield from store.read_role('foo')
    assert 'policy' in role

    deleted = yield from store.delete_role('foo')
    assert deleted

    with pytest.raises(KeyError):
        yield from store.read_role('foo')
