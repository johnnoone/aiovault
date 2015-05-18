import asyncio
import logging
from .bases import AuthBackend
from aiovault.request import Request
from aiovault.util import task


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
    def login(self, *, cert):
        method = 'POST'
        path = '/auth/%s/certs/login' % self.name
        if cert is True:
            # use current handler
            logging.info('use current certificate')
            req_handler = self.req_handler
        else:
            logging.info('exchange certificate')
            req_handler = Request(self.req_handler.addr,
                                  self.req_handler.version,
                                  self.req_handler.token,
                                  cert)
        response = yield from req_handler(method, path)
        print(response)

    @asyncio.coroutine
    def write_cert(self, name, *, certificate, display_name=None,
                   policies=None, lease=None):
        """Write certificate

        Parameters:
            name (str): The name of the certificate
            certificate (str): The public certificate that should be trusted.
                               Must be x509 PEM encoded
            display_name (str): The display name to use for clients using this
                                certificate
            policies (str): Comma-separated list of policies
            lease (str): Lease time in seconds. Defaults to 1 hour
        """
        method = 'POST'
        path = '/auth/%s/certs/%s' % (self.name, name)
        data = {'policies': policies,
                'display_name': display_name,
                'certificate': certificate,
                'lease': lease}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def read_cert(self, name):
        """Read certificate

        Parameters:
            name (str): The name of the certificate
        """
        method = 'GET'
        path = '/auth/%s/certs/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @asyncio.coroutine
    def delete_cert(self, name):
        """Delete certificate

        Parameters:
            name (str): The name of the certificate
        """
        method = 'DELETE'
        path = '/auth/%s/certs/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204
