
class PolicyEndpoint:

    def list(self):
        """Lists all the available policies.
        """
        method = 'GET'
        path = '/sys/policy'

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    def put(self, name, rules):
        """Add or update a policy.

        Once a policy is updated, it takes effect immediately to all
        associated users.

        Parameters:
            name (str): The policy name
            rules (obj): The policy document.
        """
        method = 'PUT'
        path = '/sys/policy/%s' % name
        data = {'rules': rules}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result

    def delete(self, name):
        """Delete the policy with the given name.

        This will immediately affect all associated users.

        Parameters:
            name (str): The policy name
        """
        method = 'DELETE'
        path = '/sys/policy/%s' % name

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result
