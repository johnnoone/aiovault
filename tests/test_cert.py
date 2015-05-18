from aiovault import Vault
from conftest import async_test
import pytest
import os.path


@async_test
def test_cert(dev_server, env):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    added = yield from client.auth.add('cert')
    assert added 

    store = yield from client.auth.load('cert')
    assert store.__repr__() == "<CertBackend(name='cert')>"

    filename = os.path.join(env.CERT_PATH, 'server.crt')
    with open(filename) as file:
        added = yield from store.configure_cert('foo', certificate=file.read())
        assert added

    certs = [
        os.path.join(env.CERT_PATH, 'server.key'),
        os.path.join(env.CERT_PATH, 'server.crt'),
    ]
    client2 = Vault('https://127.0.0.1:8200')
    res =  yield from client2.auth.login('cert', cert=certs)
    print(res)
    assert False
