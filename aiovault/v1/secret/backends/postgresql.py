from .bases import SecretBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import format_duration, ok, task


class PostgreSQLBackend(SecretBackend):

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
        path = self.path('config/connection')
        data = {'value': dsn}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

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
        path = self.path('config/lease')
        data = {'lease': format_duration(lease),
                'lease_max': format_duration(lease_max)}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def read_role(self, name):
        """Queries the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = self.path('roles', name)

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
        path = self.path('roles', name)
        data = {'sql': sql}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def delete_role(self, name):
        """Deletes the role definition.

        Parameters:
            name (str): The role name
        """
        method = 'DELETE'
        path = self.path('roles', name)

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def creds(self, name):
        """Generates a new set of dynamic credentials based on the named role.

        Parameters:
            name (str): The role name
        """
        method = 'GET'
        path = self.path('creds', name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)
