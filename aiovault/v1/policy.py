import json
from aiovault.exceptions import InvalidPath
from aiovault.policy import Policy
from aiovault.util import suppress, task


class PolicyEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @task
    def items(self):
        """Lists all the available policies.
        """
        method = 'GET'
        path = '/sys/policy'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result['policies']

    @task
    def read(self, name):
        """Fetch one policy by its name.

        Parameters:
            name (str): The policy name
        Returns:
            Policy: The policy
        """
        method = 'GET'
        path = '/sys/policy/%s' % name

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            name, rules = '', ''
            with suppress(KeyError, ValueError):
                name = result['name']
                rules = json.loads(result['rules']).get('path', None)
            return Policy(name=name, rules=rules)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
    def write(self, name, rules):
        """Add or update a policy.

        Once a policy is updated, it takes effect immediately to all
        associated users.

        Parameters:
            name (str): The policy name
            rules (obj): The policy document.
        Returns:
            bool: Policy has been written
        """
        method = 'PUT'
        path = '/sys/policy/%s' % name
        rules = getattr(rules, 'rules', rules)
        data = {'rules': json.dumps({'path': rules})}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def delete(self, name):
        """Delete the policy with the given name.

        This will immediately affect all associated users.

        Parameters:
            name (str): The policy name
        Returns:
            bool: Policy does not exists in storage
        """
        method = 'DELETE'
        path = '/sys/policy/%s' % name

        response = yield from self.req_handler(method, path)
        return response.status == 204
