import json
from aiovault.exceptions import InvalidPath
from aiovault.policy import Rules
from aiovault.util import suppress, ok, task, Path


class PolicyEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @property
    def path(self):
        return Path('/sys/policy')

    @task
    def items(self):
        """List the policies on the server.

        Returns:
            set: Policy names
        """
        method = 'GET'
        path = self.path

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return set(result['policies'])

    @task
    def read(self, name):
        """Read a single policy.

        Parameters:
            name (str): The policy name
        Returns:
            Rules: The rules
        """
        name = getattr(name, 'name', name)
        method = 'GET'
        path = self.path(name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            name, rules = '', ''
            with suppress(KeyError, ValueError):
                name = result['name']
                rules = json.loads(result['rules']).get('path', None)
            return Rules(name=name, rules=rules)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
    def write(self, name, rules):
        """Sets rules to the given name.

        Once a policy is updated, it takes effect immediately to all
        associated users.

        Parameters:
            name (str): The policy name
            rules (dict): The rules.
        Returns:
            bool: Rules has been written
        """
        name = getattr(name, 'name', name)
        rules = getattr(rules, 'rules', rules)
        method = 'PUT'
        path = self.path(name)
        data = {'rules': json.dumps({'path': rules})}

        response = yield from self.req_handler(method, path, json=data)
        return ok(response)

    @task
    def delete(self, name):
        """Delete the rules with the given name.

        This will immediately affect all associated users. When a user
        is associated with a policy that doesn't exist, it is identical
        to not being associated with that policy.

        Parameters:
            name (str): The policy name
        Returns:
            bool: Policy does not exists in storage
        """
        name = getattr(name, 'name', name)
        method = 'DELETE'
        path = self.path(name)

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def write_path(self, name, path, policy):
        """Set one rule to a given policy

        Parameters:
            name (str): The policy name
            path (str): The path
            policy (str): The policy
        Returns:
            bool: Path has been written
        """
        try:
            rules = yield from self.read(name)
        except KeyError:
            rules = Rules(name)

        if hasattr(path, 'path'):
            path = path.path
            if path.startswith('/'):
                path = path[1:]
        rules[path] = policy
        response = yield from self.write(name, rules=rules)
        return response

    @task
    def delete_path(self, name, path):
        """Delete one rule from a given policy

        Parameters:
            name (str): The policy name
            path (str): The path
        Returns:
            bool: Path has been deleted from policy
        """
        try:
            rules = yield from self.read(name)
            path = getattr(path, 'path', path)
            del rules[path]
        except KeyError:
            return False
        response = yield from self.write(name, rules=rules)
        return response
