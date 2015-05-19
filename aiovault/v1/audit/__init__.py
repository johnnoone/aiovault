import asyncio
from .backends import load_backend


class AuditEndpoint:
    """
    Audit backends are the components in Vault that keep a detailed log of
    all requests and response to Vault.
    Because every operation with Vault is an API request/response, the audit
    log contains every interaction with Vault, including errors.
    """

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @asyncio.coroutine
    def enable(self, name, *, type=None, description=None, **options):
        """Enable an audit backend.

        Parameters:
            name (str): The audit name
            type (str): The type of the audit backend
            description (str): A description of the audit backend for operators
            options (dict): An object of options to configure the backend.
                            This is dependent on the backend type
        Returns:
            bool
        """
        type = type or name
        obj = load_backend(type, name, req_handler=self.req_handler)
        options = obj.validate(**options)
        method = 'PUT'
        path = '/sys/audit/%s' % name
        data = {'type': type,
                'description': description,
                'options': options}
        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @asyncio.coroutine
    def disable(self, name):
        """Disable the given audit backend.

        Parameters:
            name (str): The audit name
        Returns:
            bool
        """
        method = 'DELETE'
        path = '/sys/audit/%s' % name

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @asyncio.coroutine
    def get(self, name):
        """Returns audit backend.

        Parameters:
            name (str): The audit backend name
        Returns
            dict
        """
        results = yield from self.items()
        return results['%s/' % name]

    @asyncio.coroutine
    def items(self):
        """Disable the given audit backend.
        """
        method = 'GET'
        path = '/sys/audit'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
