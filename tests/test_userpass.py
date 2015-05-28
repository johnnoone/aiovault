from aiovault import Vault
from conftest import async_test


@async_test
def test_userpass(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # enable userpass
    backend = yield from client.auth.enable('userpass')

    response = yield from backend.create('mitchellh', 'foo')
    assert response

    # raw login
    response = yield from client.write('/auth/userpass/login/mitchellh',
                                       json={"password": "foo"})
    result = yield from response.json()
    assert result['auth']['metadata'] == {'username': 'mitchellh'}

    # nicer login
    token = yield from client.auth.login('userpass',
                                         username='mitchellh',
                                         password='foo')
    assert token['metadata'] == {'username': 'mitchellh'}
