from aiovault.objects import SealStatus


class SealEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    def status(self):
        """Returns the seal status of the Vault.

        Returns:
            SealStatus: The seal status
        """
        method = 'GET'
        path = '/sys/seal-status'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return SealStatus(**result)

    def seal(self):
        """Seals the Vault.

        Returns:
            bool: Vault has been sealed
        """
        method = 'PUT'
        path = '/sys/seal'

        response = yield from self.req_handler(method, path)
        return response.status == 204

    def unseal(self, secret_shares, key):
        """Enter a single master key share to progress the unsealing of the
        Vault. If the threshold number of master key shares is reached, Vault
        will attempt to unseal the Vault. Otherwise, this API must be called
        multiple times until that threshold is met.

        Parameters:
            secret_shares (int): The number of shares to split
                                 the master key into
            key (str): A single master share key

        Returns:
            SealStatus: The seal status
        """
        method = 'PUT'
        path = '/sys/unseal'
        data = {'secret_shares': secret_shares,
                'key': key}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return SealStatus(**result)
