from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_ldap(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    response = yield from client.auth.enable('ldap')
    assert response

    auth = yield from client.auth.get('ldap')

    configured = yield from auth.configure(url='ldap://ldap.forumsys.com',
                                           userattr='uid',
                                           userdn='dc=example,dc=com',
                                           groupdn='dc=example,dc=com')
    assert configured

    writen = yield from auth.write_group(name='scientists', policies='foo')
    assert writen

    token = yield from auth.login(username='tesla', password='password')
    assert token['metadata']['username'] == 'tesla'


@async_test
def test_ldap_crud(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    response = yield from client.auth.enable('ldap')
    assert response

    auth = yield from client.auth.get('ldap')

    configured = yield from auth.configure(url='ldap://ldap.forumsys.com',
                                           userattr='uid',
                                           userdn='dc=example,dc=com',
                                           groupdn='dc=example,dc=com')
    assert configured

    writen = yield from auth.write_group(name='g1', policies='foo')
    assert writen

    data = yield from auth.read_group(name='g1')
    assert data['policies'] == 'foo'

    deleted = yield from auth.delete_group(name='g1')
    assert deleted

    with pytest.raises(KeyError):
        yield from auth.read_group(name='g1')
