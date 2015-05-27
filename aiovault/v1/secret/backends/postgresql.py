from .bases import SecretBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import format_duration, task


class PostgreSQLBackend(SecretBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @task
    def config_connection(self, *, dsn):
        """Configures the connection string used
        to communicate with PostgreSQL.

        This is a root protected endpoint.

        Parameters:
            dsn (str): The PostgreSQL connection URL or PG style string.
                       e.g. "user=foo host=bar"
        """
        method = 'POST'
        path = '/%s/config/connection' % self.name
        data = {'value': dsn}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
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
        data = {'lease': format_duration(lease),
                'lease_max': format_duration(lease_max)}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def read_role(self, name):
        """Queries the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = '/%s/roles/%s' % (self.name, name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
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

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def delete_role(self, name):
        """Deletes the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'DELETE'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @task
    def creds(self, name):
        """Generates a new set of dynamic credentials based on the named role.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = '/%s/creds/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)
