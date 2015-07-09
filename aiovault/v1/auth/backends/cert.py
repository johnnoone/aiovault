from .bases import AuthBackend
from aiovault.objects import Value
from aiovault.token import authenticate
from aiovault.util import format_duration, format_policies, ok, task


class CertBackend(AuthBackend):
    """Manage trusted certificates used for authentication.

    This endpoint allows you to create, read, update, and delete trusted
    certificates that are allowed to authenticate.

    Deleting a certificate will not revoke auth for prior authenticated
    connections. To do this, do a revoke on "login". If you don't need to
    revoke login immediately, then the next renew will cause the lease to
    expire.
    """

    @task
    def login(self):
        """
        Returns:
            LoginToken
        """
        method = 'POST'
        path = self.path('login')
        token = yield from authenticate(self.req_handler,
                                        method,
                                        path)
        return token

    @task
    def write_cert(self, name, *, certificate, display_name=None,
                   policies=None, lease=None):
        """Write certificate

        Parameters:
            name (str): The name of the certificate
            certificate (str): The public certificate that should be trusted.
                               Must be x509 PEM encoded
            display_name (str): The display name to use for clients using this
                                certificate
            policies (list): The policies
            lease (str): Lease time in seconds. Defaults to 1 hour
        """
        method = 'POST'
        path = self.path('certs', name)
        data = {'policies': format_policies(policies),
                'display_name': display_name,
                'certificate': certificate,
                'lease': format_duration(lease)}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def read_cert(self, name):
        """Read certificate

        Parameters:
            name (str): The name of the certificate
        """
        method = 'GET'
        path = self.path('certs', name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)

    @task
    def delete_cert(self, name):
        """Delete certificate

        Parameters:
            name (str): The name of the certificate
        """
        method = 'DELETE'
        path = self.path('certs', name)

        response = yield from self.req_handler(method, path)
        return ok(response)
