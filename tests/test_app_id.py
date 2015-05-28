from aiovault import Vault
from conftest import async_test


@async_test
def test_appid(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.enable('app-id')
    assert backend.__repr__() == "<AppIDBackend(name='app-id')>"

    created = yield from backend.write_app('foo', policies=['dummy'])
    assert created

    app = yield from backend.read_app('foo')
    assert app['key'] == 'foo'

    created = yield from backend.write_user('bar', app_id='foo')
    assert created

    # do login
    client = Vault(dev_server.addr)

    # login
    backend = client.auth.load('app-id')
    result = yield from backend.login(app_id='foo', user_id='bar')
    assert result['policies'] == ['dummy']


@async_test
def test_appid_raw(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # enable app-id
    response = yield from client.write('/sys/auth/app-id',
                                       json={'type': 'app-id'})
    assert response.status == 204

    response = yield from client.write('/auth/app-id/map/app-id/foo',
                                       json={'value': 'dummy'})

    response = yield from client.write('/auth/app-id/map/user-id/bar',
                                       json={'value': 'foo'})
    assert response.status == 204

    # do login
    client = Vault(dev_server.addr)

    # login
    response = yield from client.write('/auth/app-id/login',
                                       json={'app_id': 'foo',
                                             'user_id': 'bar'})
    result = yield from response.json()
    assert result['auth']['policies'] == ['dummy']
