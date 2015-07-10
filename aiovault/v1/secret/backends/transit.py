from .bases import SecretBackend
from aiovault.exceptions import InvalidPath, InvalidRequest
from aiovault.objects import Value
from aiovault.util import base64_encode, base64_decode, ok, task


class TransitBackend(SecretBackend):

    @task
    def read_key(self, name):
        """Returns information about a named encryption key.

        This is a root protected endpoint.

        Parameters:
            name (str): The transit key
        Returns:
            Value
        """
        method = 'GET'
        path = self.path('keys', name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
    def read_raw(self, name):
        """Fetch raw keys for named encryption keys.

        This path is used to get the underlying encryption keys used
        for the named keys that are available

        Parameters:
            name (str): The transit key
        Returns:
            Value
        """
        method = 'GET'
        path = self.path('raw', name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
    def write_key(self, name, *, derived=False):
        """Creates a new named encryption key.

        This is a root protected endpoint.

        Parameters:
            name (str): The transit key
            derived (bool): Enables key derivation mode. This allows
                            for per-transaction unique keys
        Returns:
            bool
        """
        method = 'POST'
        data = {'derived': derived}
        path = self.path('keys', name)

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
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
        path = self.path('keys', name)

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def encrypt(self, key, plaintext, context=None):
        """Encrypts the provided plaintext using the named key.

        Parameters:
            key (str): The transit key
            plaintext (str): The plaintext to encrypt
            context (str): Context for key derivation. Required for
                           derived keys.
        Returns:
            Value
        """
        method = 'POST'
        path = self.path('encrypt', key)
        data = {'plaintext': base64_encode(plaintext),
                'context': base64_encode(context) if context else None}

        try:
            response = yield from self.req_handler(method, path, json=data)
            result = yield from response.json()
            return Value(**result)
        except InvalidRequest as error:
            raise ValueError(error.errors.pop())

    @task
    def decrypt(self, key, ciphertext, context=None):
        """Decrypts the provided ciphertext using the named key.

        Parameters:
            key (str): The transit key
            ciphertext (str): The ciphertext to decrypt,
                              provided as returned by encrypt.
            context (bool): Context for key derivation. Required for
                            derived keys.
        Returns:
            Value
        """
        method = 'POST'
        path = self.path('decrypt', key)
        data = {'ciphertext': ciphertext,
                'context': base64_encode(context) if context else None}

        try:
            response = yield from self.req_handler(method, path, json=data)
            result = yield from response.json()
        except InvalidRequest as error:
            raise ValueError(error.errors.pop())
        result = Value(**result)
        result['plaintext'] = base64_decode(result['plaintext'])
        return result
