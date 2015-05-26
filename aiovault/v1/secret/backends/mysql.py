from .bases import SecretBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import task


class MySQLBackend(SecretBackend):
    """
    The MySQL backend dynamically generates database users.

    After mounting this backend, configure it using the endpoints
    within the "config/" path.
    """
    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @task
    def config_connection(self, *, dsn):
        """Configure the connection string to talk to MySQL

        This path configures the connection string used to connect to MySQL.
        The value of the string is a Data Source Name (DSN). An example is
        using ``username:password@protocol(address)/dbname?param=value``.

        For example, RDS may look like::

            id:password@tcp(your-amazonaws-uri.com:3306)/dbname

        When configuring the connection string, the backend will verify its
        validity.

        This is a root protected endpoint.

        Parameters:
            dsn (str): The MySQL DSN
        Returns:
            bool
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
        Returns:
            bool
        """
        method = 'POST'
        path = '/%s/config/lease' % self.name
        data = {'lease': lease,
                'lease_max': lease_max}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def read_role(self, name):
        """Queries the role definition.

        Parameters:
            name (str): Name of the role
        Returns:
            Value
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

        This path lets you manage the roles that can be created with this
        backend.

        The "sql" parameter customizes the SQL string used to create the role.
        This can be a sequence of SQL queries, each semi-colon seperated. Some
        substitution will be done to the SQL string for certain keys.
        The names of the variables must be surrounded by "{{" and "}}" to be
        replaced.

        :name: The random username generated for the DB user.
        :password: The random password generated for the DB user.

        Example of a decent SQL query to use::

          CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';
          GRANT ALL ON db1.* TO '{{name}}'@'%';

        Note the above user would be able to access anything in db1. Please see
        the MySQL manual on the GRANT command to learn how to do more fine
        grained access.

        Parameters:
            name (str): Name of the role
            sql (str): The SQL statements executed to create and configure the
                       role. Must be semi-colon separated.
        Returns:
            bool
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
        Returns:
            bool
        """
        method = 'DELETE'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @task
    def creds(self, name):
        """Generates a new set of dynamic credentials based on the named role.

        This path reads database credentials for a certain role. The database
        credentials will be generated on demand and will be automatically
        revoked when the lease is up.

        Parameters:
            name (str): The role name
        Returns:
            Value
        """
        method = 'GET'
        path = '/%s/creds/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)
