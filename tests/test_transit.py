from aiovault import Vault
from conftest import async_test
import pytest

PLAIN_TEXT = "the quick brown fox"
CONTEXT = 'my-cool-context'


@async_test
def test_basic(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('transit')
    assert mounted

    written = yield from backend.write_key('test', derived=False)
    assert written

    policy = yield from backend.read_key('test')
    assert policy['name'] == 'test'
    assert policy['derived'] is False


    policy = yield from backend.read_raw('test')
    assert policy['name'] == 'test'
    assert policy['derived'] is False

    encrypted = yield from backend.encrypt('test', PLAIN_TEXT)
    assert 'ciphertext' in encrypted
    ciphertext = encrypted['ciphertext']

    decrypted = yield from backend.decrypt('test', ciphertext)
    assert 'plaintext' in decrypted
    assert decrypted['plaintext'] == PLAIN_TEXT

    deleted = yield from backend.delete_key('test')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_key('test')

    with pytest.raises(KeyError):
        yield from backend.read_raw('test')


@async_test
def test_upsert(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('transit')
    assert mounted

    with pytest.raises(KeyError):
        yield from backend.read_key('test')

    encrypted = yield from backend.encrypt('test', PLAIN_TEXT)
    assert 'ciphertext' in encrypted
    ciphertext = encrypted['ciphertext']

    policy = yield from backend.read_key('test')
    assert policy['name'] == 'test'
    assert policy['derived'] is False

    decrypted = yield from backend.decrypt('test', ciphertext)
    assert 'plaintext' in decrypted
    assert decrypted['plaintext'] == PLAIN_TEXT

    deleted = yield from backend.delete_key('test')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_key('test')


@async_test
def test_derived(dev_server):
    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('transit')
    assert mounted

    written = yield from backend.write_key('test', derived=True)
    assert written

    policy = yield from backend.read_key('test')
    assert policy['name'] == 'test'
    assert policy['derived'] is True


    policy = yield from backend.read_raw('test')
    assert policy['name'] == 'test'
    assert policy['derived'] is True

    encrypted = yield from backend.encrypt('test', PLAIN_TEXT, context=CONTEXT)
    assert 'ciphertext' in encrypted
    ciphertext = encrypted['ciphertext']

    decrypted = yield from backend.decrypt('test', ciphertext, context=CONTEXT)
    assert 'plaintext' in decrypted
    assert decrypted['plaintext'] == PLAIN_TEXT

    deleted = yield from backend.delete_key('test')
    assert deleted

    with pytest.raises(KeyError):
        yield from backend.read_key('test')

    with pytest.raises(KeyError):
        yield from backend.read_raw('test')


@async_test
def test_shortcut(dev_server):
    """docstring for test_shortcut"""
    client = Vault(dev_server.addr, token=dev_server.root_token)
    mounted, backend = yield from client.secret.mount('transit')
    assert mounted

    backend = client.secret.transit

    written = yield from backend.write_key('test')
    assert written
    #
    # policy = yield from backend.read_key('test')
    # assert policy['name'] == 'test'
    #
    # encrypted = yield from backend.encrypt('test', PLAIN_TEXT)
    # assert 'ciphertext' in encrypted
    # ciphertext = encrypted['ciphertext']
    #
    # decrypted = yield from backend.decrypt('test', ciphertext)
    # assert 'plaintext' in decrypted
    # assert decrypted['plaintext'] == PLAIN_TEXT
    #
    # deleted = yield from backend.delete_key('test')
    # assert deleted
    #
    # with pytest.raises(KeyError):
    #     yield from backend.read_key('test')
