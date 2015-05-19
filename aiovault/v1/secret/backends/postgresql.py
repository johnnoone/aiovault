import asyncio
from .bases import SecretBackend


class PostgreSQLBackend(SecretBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def config_connection(self, connection, value):
        """Configures the connection string used
        to communicate with PostgreSQL.

        This is a root protected endpoint.

        Parameters:
            value (str): The PostgreSQL connection URL or PG
                         style string. e.g. "user=foo host=bar"
        """
        method = 'POST'
        path = '/%s/config/connection' % self.name
        data = {'value': value}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def config_lease(self, lease, lease_max):
        """Configures the lease settings for generated credentials.

        If not configured, leases default to 1 hour.
        This is a root protected endpoint.

        Parameters:
            lease (str): The lease value provided as a string duration
                         with time suffix. Hour is the largest suffix.
            lease_max (str): The maximum lease value provided as a string
                             duration with time suffix. Hour is the largest
                             suffix.
        """
        method = 'POST'
        path = '/%s/config/lease' % self.name
        data = {'lease': lease,
                'lease_max': lease_max}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def read_role(self, name):
        """Queries the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def write_role(self, name, sql):
        """Creates or updates the role definition.

        Parameters:
            sql (str): The SQL statements executed to create and configure
                       the role. Must be semi-colon separated. The '{{name}}',
                       '{{password}}' and '{{expiration}}' values will be
                       substituted.
        """
        method = 'POST'
        path = '/%s/roles/%s' % (self.name, name)
        data = {'sql': sql}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def delete_role(self, name):
        """Deletes the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'DELETE'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def creds(self, name):
        """Generates a new set of dynamic credentials based on the named role.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = '/%s/creds/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
