from aiovault import Vault
from conftest import async_test
import pytest


MYSQL_SQL = """
CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';
GRANT SELECT ON *.* TO '{{name}}'@'%';
"""


@async_test
def test_basic(dev_server, env):
    try:
        dsn = env.MYSQL_DSN
    except AttributeError:
        return 'MYSQL_DSN must be set for acceptance tests'

    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('mysql')
    assert mounted

    configured = yield from backend.config_connection(dsn=dsn)
    assert configured

    configured = yield from backend.config_lease('1m', '1m')
    assert configured

    configured = yield from backend.write_role('web', sql=MYSQL_SQL)
    assert configured

    data = yield from backend.creds('web')
    assert 'username' in data
    assert 'password' in data

    # TODO remove user


@async_test
def test_crud(dev_server, env):
    try:
        dsn = env.MYSQL_DSN
    except AttributeError:
        return 'MYSQL_DSN must be set for acceptance tests'

    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('mysql')
    assert mounted

    configured = yield from backend.config_connection(dsn=dsn)
    assert configured

    configured = yield from backend.write_role('web', sql=MYSQL_SQL)
    assert configured

    role = yield from backend.read_role('web')
    assert 'sql' in role

    deleted = yield from backend.delete_role('web')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_role('web')
