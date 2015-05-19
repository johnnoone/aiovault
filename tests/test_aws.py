from aiovault import Vault, LoginError
from conftest import async_test
import pytest

AWS_POLICY = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1426528957000",
            "Effect": "Allow",
            "Action": [
                "noop:noop"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}'''


@async_test
def test_basic(dev_server, env):
    try:
        access_key = env.AWS_ACCESS_KEY_ID
        secret_key = env.AWS_SECRET_ACCESS_KEY
        region = env.AWS_DEFAULT_REGION
    except AttributeError:
        return 'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY \
               or AWS_DEFAULT_REGION missing'

    client = Vault(dev_server.addr, token=dev_server.root_token)
    added = yield from client.secret.mount('aws')
    assert added

    store = yield from client.secret.get('aws')
    configured = yield from store.config_root(access_key=access_key,
                                              secret_key=secret_key,
                                              region=region)
    assert configured

    configured = yield from store.config_lease(lease='1m',
                                               lease_max='1m')
    assert configured

    configured = yield from store.write_role('foo', policy=AWS_POLICY)
    assert configured

    data = yield from store.creds('foo')
    assert 'access_key' in data
    assert 'secret_key' in data


@async_test
def test_crud(dev_server, env):
    try:
        access_key = env.AWS_ACCESS_KEY_ID
        secret_key = env.AWS_SECRET_ACCESS_KEY
        region = env.AWS_DEFAULT_REGION
    except AttributeError:
        return 'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY \
               or AWS_DEFAULT_REGION missing'

    client = Vault(dev_server.addr, token=dev_server.root_token)
    added = yield from client.secret.mount('aws')
    assert added

    store = yield from client.secret.get('aws')
    configured = yield from store.config_root(access_key=access_key,
                                              secret_key=secret_key,
                                              region=region)
    assert configured

    configured = yield from store.config_lease(lease='1m',
                                               lease_max='1m')
    assert configured

    configured = yield from store.write_role('test', policy=AWS_POLICY)
    assert configured

    role = yield from store.read_role('test')
    assert 'policy' in role

    deleted = yield from store.delete_role('test')
    assert deleted

    with pytest.raises(KeyError):
        yield from store.read_role('test')
