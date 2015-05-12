
class LeaseEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    def renew(self, lease_id, increment=None):
        """Renew a secret, requesting to extend the lease.

        Parameters:
            lease_id (str): The lease id
            increment (int): A requested amount of time in seconds
                             to extend the lease. This is advisory.
        """
        method = 'PUT'
        path = '/sys/renew/%s' % lease_id
        data = {'increment': increment}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    def revoke(self, lease_id):
        """Revoke a secret immediately.

        Parameters:
            lease_id (str): The lease id
        """
        method = 'PUT'
        path = '/sys/revoke/%s' % lease_id

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def revoke_prefix(self, path_prefix):
        """Revoke all secrets generated under a given prefix immediately.

        Parameters:
            path_prefix (str): The path prefix
        """
        method = 'PUT'
        path = '/sys/revoke-prefix/%s' % path_prefix

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
