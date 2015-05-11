
class SysEndpoint:

    def status(self):
        """Return the initialization status of a Vault
        """

        method = 'GET'
        path = '/sys/init'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

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
        """
        method = 'PUT'
        path = '/sys/init'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def leader(self):
        """Returns the high availability status and current leader
        instance of Vault.
        """
        method = 'GET'
        path = '/sys/leader'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def health(self):
        """Returns the health status of Vault.

        This matches the semantics of a Consul HTTP health check and provides
        a simple way to monitor the health of a Vault instance.
        """
        method = 'GET'
        path = '/sys/health'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
