import json
from aiovault.exceptions import InvalidPath
from aiovault.objects import Policy
from contextlib import suppress


class PolicyEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    def items(self):
        """Lists all the available policies.
        """
        method = 'GET'
        path = '/sys/policy'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result['policies']

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
            with suppress(KeyError, ValueError):
                result['rules'] = json.loads(result['rules'])
            return Policy(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

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
        data = {'rules': json.dumps(rules)}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

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
