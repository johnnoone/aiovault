from aiovault import Vault
from conftest import async_test
import os.path

HERE = os.path.dirname(os.path.abspath(__file__))


@async_test
def test_cert(server, env):
    client = Vault(server.addr, cert=[server.csr, server.key])
    state = yield from client.initialize(secret_shares=5, secret_threshold=3)
    yield from client.seal.unseal(state.keys)
    yield from client.audit.enable('file', path='/tmp/aiovault.log')

    backend = yield from client.auth.enable('cert')
    assert backend.__repr__() == "<CertBackend(name='cert')>"

    crt_file = os.path.join(HERE, 'certs2', 'server.crt')
    csr_file = os.path.join(HERE, 'certs2', 'server.csr')
    key_file = os.path.join(HERE, 'certs2', 'server.key')

    with open(crt_file) as file:
        written = yield from backend.write_cert('foo',
                                                certificate=file.read(),
                                                policies=['pierre', 'pol'])
        assert written

    data = yield from backend.read_cert('foo')
    assert 'pierre' in data['policies']

    # TODO does not work with Vault v0.1.2
    return

    client = Vault(server.addr, cert=[csr_file, key_file])
    backend = client.auth.load('cert')
    res = yield from backend.login()
    print(res)
