from aiovault import Vault, VaultCLI
from conftest import async_test
import pytest


@async_test
def test_init_cli(server):
    cli = VaultCLI(server)
    cli.initialize()
    cli.unseal()
    cli.audit_file(path='/tmp/aiovault.log')


@pytest.mark.xfail
@async_test
def test_init(server):
    client = Vault(server.addr, cert=[server.csr, server.key])
    print(client)

    response = yield from client.status()
    print(response)

    state = yield from client.initialize(secret_shares=5, secret_threshold=3)
    assert hasattr(state, 'root_token')
    assert hasattr(state, 'keys')

    status = yield from client.seal.status()
    assert status.sealed is True
    status = yield from client.seal.unseal(state.keys)
    assert status.sealed is False
