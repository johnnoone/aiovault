import asyncio
from .bases import SecretBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import base64_encode, base64_decode


class TransitBackend(SecretBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def read_key(self, name):
        """Returns information about a named encryption key.

        This is a root protected endpoint.

        Parameters:
            name (str): The transit key
        Returns:
            Value
        """
        method = 'GET'
        path = '/%s/keys/%s' % (self.name, name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @asyncio.coroutine
    def write_key(self, name):
        """Creates a new named encryption key.

        This is a root protected endpoint.

        Parameters:
            name (str): The transit key
        Returns:
            bool
        """
        method = 'POST'
        path = '/%s/keys/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @asyncio.coroutine
    def delete_key(self, name):
        """Deletes a named encryption key.

        This is a root protected endpoint.
        All data encrypted with the named key will no longer be decryptable.

        Parameters:
            name (str): The transit key
        Returns:
            bool
        """
        method = 'DELETE'
        path = '/%s/keys/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @asyncio.coroutine
    def encrypt(self, key, plaintext):
        """Encrypts the provided plaintext using the named key.

        Parameters:
            key (str): The transit key
            plaintext (str): The plaintext to encrypt
        Returns:
            Value
        """
        method = 'POST'
        path = '/%s/encrypt/%s' % (self.name, key)
        data = {'plaintext': base64_encode(plaintext)}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return Value(**result)

    @asyncio.coroutine
    def decrypt(self, key, ciphertext):
        """Decrypts the provided ciphertext using the named key.

        Parameters:
            key (str): The transit key
            ciphertext (str): The ciphertext to decrypt,
                              provided as returned by encrypt.
        Returns:
            Value
        """
        method = 'POST'
        path = '/%s/decrypt/%s' % (self.name, key)
        data = {'ciphertext': ciphertext}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        result = Value(**result)
        result['plaintext'] = base64_decode(result['plaintext'])
        return result
