from aiovault.objects import SealStatus
from aiovault.util import ok, task


class SealEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @task
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

    @task
    def seal(self):
        """Seals the Vault.

        Returns:
            bool: Vault has been sealed
        """
        method = 'PUT'
        path = '/sys/seal'

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def unseal(self, keys):
        """Enter master keys share to progress the unsealing of the Vault.
        If the threshold number of master key shares is reached, Vault will
        attempt to unseal the Vault. Otherwise, this API must be called
        multiple times until that threshold is met.

        Parameters:
            keys (list): A list of master share key
            secret_shares (int): The number of shares to split
                                 the master key into

        Returns:
            SealStatus: The seal status
        """
        method = 'PUT'
        path = '/sys/unseal'

        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            data = {'key': key}

            response = yield from self.req_handler(method, path, json=data)
            result = yield from response.json()
            status = SealStatus(**result)
            if not status.sealed:
                break
        return status
