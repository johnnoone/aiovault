from aiovault import Vault
from conftest import async_test
import pytest
import os.path


@async_test
def test_cert(dev_server, env):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.enable('cert')
    assert backend.__repr__() == "<CertBackend(name='cert')>"

    filename = os.path.join(env.CERT_PATH, 'server.crt')
    with open(filename) as file:
        written = yield from backend.write_cert('foo',
                                                certificate=file.read(),
                                                policies=['pierre', 'pol'])
        assert written

    data = yield from backend.read_cert('foo')
    print(data)
    certs = [
        os.path.join(env.CERT_PATH, 'server.crt'),
        os.path.join(env.CERT_PATH, 'server.key'),
    ]
    client = Vault('https://127.0.0.1:8200')
    backend = client.auth.load('cert')
    res = yield from backend.login(cert=certs)
    print(res)
    assert False


@pytest.mark.skipif(True, reason="not ready")
@async_test
def test_cert_ca(dev_server, env):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    backend = yield from client.auth.enable('cert')
    assert backend.__repr__() == "<CertBackend(name='cert')>"

    filename = os.path.join(env.CERT_PATH, 'ca', 'root.cer')
    with open(filename) as file:
        added = yield from backend.write_cert('web',
                                              certificate=file.read(),
                                              policies='foo')
        assert added

    certs = [
        os.path.join(env.CERT_PATH, 'key', 'ourdomain.cer'),
        os.path.join(env.CERT_PATH, 'key', 'ourdomain.key'),
    ]
    client = Vault('http://127.0.0.1:8200')
    backend = client.auth.load('cert')
    res = yield from backend.login('cert', cert=certs)
    print(res)
    assert False
