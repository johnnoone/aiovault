from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_ldap(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.enable('ldap')

    configured = yield from backend.configure(url='ldap://ldap.forumsys.com',
                                              userattr='uid',
                                              userdn='dc=example,dc=com',
                                              groupdn='dc=example,dc=com')
    assert configured

    writen = yield from backend.write_group(name='scientists', policies='foo')
    assert writen

    token = yield from backend.login(username='tesla', password='password')
    assert token['metadata']['username'] == 'tesla'


@async_test
def test_ldap_crud(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.enable('ldap')

    configured = yield from backend.configure(url='ldap://ldap.forumsys.com',
                                              userattr='uid',
                                              userdn='dc=example,dc=com',
                                              groupdn='dc=example,dc=com')
    assert configured

    writen = yield from backend.write_group(name='g1', policies='foo')
    assert writen

    data = yield from backend.read_group(name='g1')
    assert data['policies'] == 'foo'

    deleted = yield from backend.delete_group(name='g1')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_group(name='g1')
