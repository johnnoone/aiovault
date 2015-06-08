from aiovault import Vault
from conftest import async_test
import os.path
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.xfail
@async_test
def test_cert(server, env):
    crt_file = os.path.join(HERE, 'certs', 'client.crt')
    csr_file = os.path.join(HERE, 'certs', 'client.csr')
    key_file = os.path.join(HERE, 'certs', 'client.key')
    ca_path = os.path.join(HERE, 'certs')

    client = Vault(server.addr, cert=[server.csr, server.key])
    state = yield from client.initialize(secret_shares=5, secret_threshold=3)
    yield from client.seal.unseal(state.keys)
    yield from client.audit.enable('file', path='/tmp/aiovault.log')

    backend = yield from client.auth.enable('cert')
    assert backend.__repr__() == "<CertBackend(name='cert')>"

    with open(csr_file) as file:
        written = yield from backend.write_cert('foo',
                                                certificate=file.read(),
                                                policies=['pierre', 'pol'])
        assert written

    data = yield from backend.read_cert('foo')
    assert 'pierre' in data['policies']

    # TODO does not work with Vault v0.1.2
    # return

    client = Vault(server.addr, cert=[crt_file, key_file, ca_path])
    backend = client.auth.load('cert')
    res = yield from backend.login()
    print(res)
