
class SealEndpoint:

    def status(self):
        """Returns the seal status of the Vault.
        """
        method = 'GET'
        path = '/sys/seal-status'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def seal(self):
        """Seals the Vault.
        """
        method = 'PUT'
        path = '/sys/seal'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def unseal(self, secret_shares, key):
        """Enter a single master key share to progress the unsealing of the
        Vault. If the threshold number of master key shares is reached, Vault
        will attempt to unseal the Vault. Otherwise, this API must be called
        multiple times until that threshold is met.

        Parameters:
            secret_shares (int): The number of shares to split
                                 the master key into.
            key (str): A single master share key.
        """
        method = 'PUT'
        path = '/sys/unseal'
        data = {'secret_shares': secret_shares,
                'key': key}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result
