from .backends import load_backend
from aiovault.util import ok, task, Path


class AuditEndpoint:
    """
    Audit backends are the components in Vault that keep a detailed log of
    all requests and response to Vault.
    Because every operation with Vault is an API request/response, the audit
    log contains every interaction with Vault, including errors.
    """

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @property
    def path(self):
        return Path('/sys/audit')

    @task
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
        path = self.path(name)
        data = {'type': type,
                'description': description,
                'options': options}
        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def disable(self, name):
        """Disable the given audit backend.

        Parameters:
            name (str): The audit name
        Returns:
            bool
        """
        method = 'DELETE'
        path = self.path(name)

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def get(self, name):
        """Returns audit backend.

        Parameters:
            name (str): The audit backend name
        Returns
            dict
        """
        results = yield from self.items()
        return results['%s/' % name]

    @task
    def items(self):
        """Disable the given audit backend.
        """
        method = 'GET'
        path = self.path

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
