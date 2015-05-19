from aiovault import Vault
from conftest import async_test
import pytest


@async_test
def test_audit_syslog(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # enable syslog
    enabled = yield from client.audit.enable('syslog')
    assert enabled

    backends = yield from client.audit.items()
    assert 'syslog/' in backends

    backend = yield from client.audit.get('syslog')
    print(backend)

    disabled = yield from client.audit.disable('syslog')
    assert disabled

    with pytest.raises(KeyError):
        yield from client.audit.get('syslog')

    backends = yield from client.audit.items()
    assert 'syslog/' not in backends


@async_test
def test_audit_file(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    # enable syslog
    enabled = yield from client.audit.enable('file', path='/tmp/testvault.log')
    assert enabled

    backends = yield from client.audit.items()
    assert 'file/' in backends

    backend = yield from client.audit.get('file')
    print(backend)

    disabled = yield from client.audit.disable('file')
    assert disabled

    with pytest.raises(KeyError):
        yield from client.audit.get('file')

    backends = yield from client.audit.items()
    assert 'file/' not in backends
