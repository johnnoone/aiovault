import asyncio
from aiovault.objects import Status, Initial, HighAvailibility, Health


class SysEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @asyncio.coroutine
    def status(self):
        """Return the initialization status of a Vault

        Returns:
            Status: vault server status
        """

        method = 'GET'
        path = '/sys/init'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Status(**result)

    @asyncio.coroutine
    def initialize(self, secret_shares, secret_threshold):
        """Initializes a new Vault.

        The Vault must've not been previously initialized

        Parameters:
            secret_shares (int): The number of shares to split
                                 the master key into.
            secret_threshold (int): The number of shares required
                                    to reconstruct the master key.
                                    This must be less than or equal
                                    to secret_shares.
        Returns:
            Initial: Includes the master keys and initial root token
        """
        method = 'PUT'
        path = '/sys/init'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Initial(**result)

    @asyncio.coroutine
    def leader(self):
        """Returns the high availability status and current leader
        instance of Vault.

        Returns:
            HighAvailibility: High availibility status
        """
        method = 'GET'
        path = '/sys/leader'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return HighAvailibility(**result)

    @asyncio.coroutine
    def health(self):
        """Returns the health status of Vault.

        This matches the semantics of a Consul HTTP health check and
        provides a simple way to monitor the health of a Vault instance.

        Returns:
            Health: health status
        """
        method = 'GET'
        path = '/sys/health'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Health(**result)
