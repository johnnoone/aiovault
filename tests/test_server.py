from aiovault import Vault
from conftest import async_test


@async_test
def test_init(server):
    client = Vault(server.addr, cert=[server.csr, server.key])
    print(client)

    # list mounted backends
    response = yield from client.initialize(secret_shares=2,
                                            secret_threshold=2)
    print(response)

    assert False
