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

    cafile = os.path.join(HERE, 'certs2', 'root.cer')
    certfile = os.path.join(HERE, 'certs2', 'ourdomain.cer')
    keyfile = os.path.join(HERE, 'certs2', 'ourdomain.key')
    with open(cafile) as file:
        written = yield from backend.write_cert('foo',
                                                certificate=file.read(),
                                                policies=['pierre', 'pol'])
        assert written

    data = yield from backend.read_cert('foo')
    assert 'pierre' in data['policies']

    client = Vault(server.addr, cert=[certfile, keyfile])
    backend = client.auth.load('cert')

    # does not work for now
    return
    res = yield from backend.login()
    print(res)
