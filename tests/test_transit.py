from aiovault import Vault
from conftest import async_test
import pytest

PLAIN_TEXT = "the quick brown fox"


@async_test
def test_basic(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    added = yield from client.secret.mount('transit')
    assert added

    store = yield from client.secret.get('transit')
    written = yield from store.write_key('test')
    assert written

    policy = yield from store.read_key('test')
    assert policy['name'] == 'test'

    encrypted = yield from store.encrypt('test', PLAIN_TEXT)
    assert 'ciphertext' in encrypted
    ciphertext = encrypted['ciphertext']

    decrypted = yield from store.decrypt('test', ciphertext)
    assert 'plaintext' in decrypted
    assert decrypted['plaintext'] == PLAIN_TEXT

    deleted = yield from store.delete_key('test')
    assert deleted

    with pytest.raises(KeyError):
        data = yield from store.read_key('test')
        assert data['name'] == 'test'
