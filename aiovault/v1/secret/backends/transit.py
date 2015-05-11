import asyncio
from .bases import SecretBackend


class TransitBackend(SecretBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def get_key(self, name):
        """Returns information about a named encryption key.

        This is a root protected endpoint.

        Parameters:
            name (str): The transit key
        """
        method = 'GET'
        path = '/%s/keys/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def create_key(self, name):
        """Creates a new named encryption key.

        This is a root protected endpoint.

        Parameters:
            name (str): The transit key
        """
        method = 'POST'
        path = '/%s/keys/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def delete_key(self, name):
        """Deletes a named encryption key.

        This is a root protected endpoint.
        All data encrypted with the named key will no longer be decryptable.

        Parameters:
            name (str): The transit key
        """
        method = 'DELETE'
        path = '/%s/keys/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def encrypt(self, key, plaintext):
        """Encrypts the provided plaintext using the named key.

        Parameters:
            key (str): The transit key
            plaintext (str): The plaintext to encrypt,
                             provided as base64 encoded
        """
        method = 'POST'
        path = '/%s/encrypt/%s' % (self.name, key)
        data = {'plaintext': plaintext}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def decrypt(self, key, ciphertext):
        """Decrypts the provided ciphertext using the named key.

        Parameters:
            key (str): The transit key
            ciphertext (str): The ciphertext to decrypt,
                              provided as returned by encrypt.
        """
        method = 'POST'
        path = '/%s/decrypt/%s' % (self.name, key)
        data = {'ciphertext': ciphertext}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result
