from aiovault import Vault
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
    mounted, backend = yield from client.secret.mount('aws')
    configured = yield from backend.config_root(access_key=access_key,
                                                secret_key=secret_key,
                                                region=region)
    assert configured

    configured = yield from backend.config_lease(lease='1m',
                                                 lease_max='1m')
    assert configured

    configured = yield from backend.write_role('foo', policy=AWS_POLICY)
    assert configured

    data = yield from backend.creds('foo')
    assert 'access_key' in data
    assert 'secret_key' in data

    # TODO destroy the new account with boto


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
    mounted, backend = yield from client.secret.mount('aws')
    configured = yield from backend.config_root(access_key=access_key,
                                                secret_key=secret_key,
                                                region=region)
    assert configured

    configured = yield from backend.config_lease(lease='1m', lease_max='1m')
    assert configured

    configured = yield from backend.write_role('test', policy=AWS_POLICY)
    assert configured

    role = yield from backend.read_role('test')
    assert 'policy' in role

    deleted = yield from backend.delete_role('test')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_role('test')
