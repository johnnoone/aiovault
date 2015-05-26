from aiovault.objects import Value
from aiovault.util import task


class LeaseEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @task
    def renew(self, lease_id, increment=None):
        """Renew a secret, requesting to extend the lease.

        Parameters:
            lease_id (str): The lease id
            increment (int): A requested amount of time in seconds
                             to extend the lease. This is advisory.
        Returns:
            Value
        """
        method = 'PUT'
        path = '/sys/renew/%s' % lease_id
        data = {'increment': increment}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return Value(**result)

    @task
    def revoke(self, lease_id):
        """Revoke a secret immediately.

        Parameters:
            lease_id (str): The lease id
        Returns:
            bool
        """
        method = 'PUT'
        path = '/sys/revoke/%s' % lease_id

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @task
    def revoke_prefix(self, path_prefix):
        """Revoke all secrets generated under a given prefix immediately.

        Parameters:
            path_prefix (str): The path prefix
        Returns:
            bool
        """
        method = 'PUT'
        path = '/sys/revoke-prefix/%s' % path_prefix

        response = yield from self.req_handler(method, path)
        return response.status == 204
