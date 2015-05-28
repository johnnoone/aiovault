from aiovault import Vault
from conftest import async_test
import pytest
import os.path

# @async_test
# def test_cert(dev_server, env):
#     client = Vault(dev_server.addr, token=dev_server.root_token)
#
#     added = yield from client.auth.enable('cert')
#     assert added
#
#     store = client.auth.load('cert')
#     assert store.__repr__() == "<CertBackend(name='cert')>"
#
#     filename = os.path.join(env.CERT_PATH, 'server.crt')
#     with open(filename) as file:
#         added = yield from store.write_cert('foo', certificate=file.read())
#         assert added
#
#     certs = [
#         os.path.join(env.CERT_PATH, 'server.key'),
#         os.path.join(env.CERT_PATH, 'server.crt'),
#     ]
#     client2 = Vault('https://127.0.0.1:8200')
#     res =  yield from client2.auth.login('cert', cert=certs)
#     print(res)
#     assert False


@pytest.mark.skipif(True, reason="not ready")
@async_test
def test_cert_ca(dev_server, env):
    client = Vault(dev_server.addr, token=dev_server.root_token)

    added = yield from client.auth.enable('cert')
    assert added

    store = client.auth.load('cert')
    assert store.__repr__() == "<CertBackend(name='cert')>"

    filename = os.path.join(env.CERT_PATH, 'ca', 'root.cer')
    with open(filename) as file:
        added = yield from store.write_cert('web',
                                            certificate=file.read(),
                                            policies='foo')
        assert added

    certs = [
        os.path.join(env.CERT_PATH, 'key', 'ourdomain.cer'),
        os.path.join(env.CERT_PATH, 'key', 'ourdomain.key'),
    ]
    client2 = Vault('http://127.0.0.1:8200')
    res = yield from client2.auth.login('cert', cert=certs)
    print(res)
    assert False
