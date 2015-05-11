from .backends import load_backend


class AuditEndpoint:
    """
    Audit backends are the components in Vault that keep a detailed log of
    all requests and response to Vault.
    Because every operation with Vault is an API request/response, the audit
    log contains every interaction with Vault, including errors.
    """

    def put(self, name, type, description=None, **options):
        """Enable an audit backend.

        Parameters:
            name (str): The audit name
            type (str): The type of the audit backend
            description (str): A description of the audit backend for operators
            options (dict): An object of options to configure the backend.
                            This is dependent on the backend type
        """

        obj = load_backend(type, name, self.req_handler)
        options = obj.validate(**options)
        method = 'PUT'
        path = '/sys/audit/%s' % name
        data = {'type': type,
                'description': description,
                'options': options}
        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    def delete(self, name):
        """Disable the given audit backend.

        Parameters:
            name (str): The audit name
        """
        method = 'DELETE'
        path = '/sys/audit/%s' % name

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
