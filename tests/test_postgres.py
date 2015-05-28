from aiovault import Vault
from conftest import async_test
import pytest


PG_SQL = """
CREATE ROLE "{{name}}" WITH
  LOGIN
  PASSWORD '{{password}}'
  VALID UNTIL '{{expiration}}';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{{name}}";
"""


@async_test
def test_basic(dev_server, env):
    try:
        dsn = env.PG_URL
    except AttributeError:
        return 'PG_URL must be set for acceptance tests'

    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('postgresql')
    assert mounted

    configured = yield from backend.config_connection(dsn=dsn)
    assert configured

    configured = yield from backend.config_lease('1m', '1m')
    assert configured

    configured = yield from backend.write_role('web', sql=PG_SQL)
    assert configured

    data = yield from backend.creds('web')
    assert 'username' in data
    assert 'password' in data

    # TODO remove user


@async_test
def test_crud(dev_server, env):
    try:
        dsn = env.PG_URL
    except AttributeError:
        return 'PG_URL must be set for acceptance tests'

    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('postgresql')
    assert mounted

    configured = yield from backend.config_connection(dsn=dsn)
    assert configured

    configured = yield from backend.write_role('web', sql=PG_SQL)
    assert configured

    role = yield from backend.read_role('web')
    assert 'sql' in role

    deleted = yield from backend.delete_role('web')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_role('web')
