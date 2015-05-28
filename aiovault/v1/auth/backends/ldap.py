from .bases import AuthBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.token import authenticate
from aiovault.util import format_policies, task


class LDAPBackend(AuthBackend):

    @task
    def login(self, *, username, password):
        """Log with ldap.

        Parameters:
            username (str): DN (distinguished name) to be used for login
            password (str): Password for this user
        Returns:
            LoginToken
        """
        method = 'POST'
        path = '/auth/%s/login/%s' % (self.name, username)
        data = {'password': password}

        token = yield from authenticate(self.req_handler,
                                        method,
                                        path,
                                        json=data)
        return token

    @task
    def configure(self, url, userattr, userdn, groupdn):
        """Configure the LDAP server to connect to.

        This endpoint allows you to configure the LDAP server to connect to,
        and give basic information of the schema of that server.

        The LDAP URL can use either the "ldap://" or "ldaps://" schema. In the
        former case, an unencrypted connection will be done, with default port
        389; in the latter case, a SSL connection will be done, with default
        port 636.

        Parameters:
            url (str): ldap URL to connect to (default: ldap://127.0.0.1)
            userattr (str): Attribute used for users (default: cn)
            userdn (str): LDAP domain to use for users
                          (eg: ou=People,dc=example,dc=org)
            groupdn (str): LDAP domain to use for groups
                           (eg: ou=Groups,dc=example,dc=org)
        Returns:
            bool
        """
        method = 'POST'
        path = '/auth/%s/config' % self.name
        data = {'url': url,
                'userattr': userattr,
                'userdn': userdn,
                'groupdn': groupdn}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def read_group(self, name):
        """Show group.

        Parameters:
            name (str): Name of the LDAP group
        Returns:
            Value
        """
        method = 'GET'
        path = '/auth/%s/groups/%s' % (self.name, name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
    def write_group(self, name, policies):
        """Manage users allowed to authenticate.

        This endpoint allows you to set configuration for a LDAP group
        that is allowed to authenticate, and associate policies to them.

        Parameters:
            name (str): Name of the LDAP group
            policies (str): Comma-separated list of policies associated
                            to the group
        Returns:
            bool
        """
        method = 'POST'
        path = '/auth/%s/groups/%s' % (self.name, name)
        data = {'policies': format_policies(policies)}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def delete_group(self, name):
        """Delete group.

        Deleting group will not revoke auth for prior authenticated users in
        that group. To do this, do a revoke on "login/<username>" for the
        usernames you want revoked.

        Parameters:
            name (str): Name of the LDAP group
        Returns:
            bool
        """
        method = 'DELETE'
        path = '/auth/%s/groups/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204
