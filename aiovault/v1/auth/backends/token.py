from aiovault.exceptions import InvalidPath
from aiovault.token import ReadToken, LoginToken
from aiovault.util import format_duration, ok, task, Path, extract_id


class TokenBackend:

    def __init__(self, name, type, req_handler):
        self.name = name
        self.type = type  # this is silly
        self.req_handler = req_handler

    @property
    def path(self):
        return Path('/auth/%s' % self.name)

    @task
    def create(self, *, id=None, policies=None, metadata=None, no_parent=None,
               lease=None, display_name=None, num_uses=None):
        """Creates a new token.

        Certain options are only available to when called by a root token.

        Parameters:
            id (str): The ID of the client token. Can only be specified by a
                      root token. Otherwise, the token ID is a randomly
                      generated UUID.
            policies (list): A list of policies for the token. This must be a
                             subset of the policies belonging to the token
                             making the request, unless root. If not specified,
                             defaults to all the policies of the calling token.
            metadata (dict) A map of string to string valued metadata.
                            This is passed through to the audit backends.
            no_parent (bool): If true and set by a root caller, the token will
                              not have the parent token of the caller. This
                              creates a token with no parent.
            lease (str): The lease period of the token, provided as "1h", where
                         hour is the largest suffix. If not provided, the token
                         is valid indefinitely.
            display_name (str): The display name of the token. Defaults to
                                "token".
            num_uses (int): The maximum uses for the given token. This can be
                            used to create a one-time-token or limited use
                            token. Defaults to 0, which has no limit to number
                            of uses.
        Returns:
            LoginToken: The client token
        """
        method = 'POST'
        path = self.path('create')
        data = {'id': id,
                'policies': policies,
                'metadata': metadata,
                'no_parent': no_parent,
                'lease': format_duration(lease),
                'display_name': display_name,
                'num_uses': num_uses}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return LoginToken(**result)

    @task
    def lookup_self(self):
        """Returns information about the current client token.

        Returns:
            ReadToken: The current client token
        """
        method = 'GET'
        path = self.path('lookup-self')

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return ReadToken(**result)

    @task
    def lookup(self, token):
        """Returns information about a client token.

        Parameters:
            token (str): The token ID
        Returns:
            ReadToken: The client token
        """
        token = extract_id(token)
        method = 'GET'
        path = self.path('lookup', token)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return ReadToken(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % token)

    @task
    def revoke(self, token):
        """Revokes a token and all child tokens.

        When the token is revoked, all secrets generated with it are also
        revoked.

        Parameters:
            token (str): The token ID
        """
        token = extract_id(token)
        method = 'POST'
        path = self.path('revoke', token)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @task
    def revoke_orphan(self, token):
        """Revokes a token but not its child tokens.

        When the token is revoked, all secrets generated with it are also
        revoked. All child tokens are orphaned, but can be revoked
        sub-sequently using :py:meth:`revoke`.

        Parameters:
            token (str): The token ID
        """
        token = extract_id(token)
        method = 'POST'
        path = self.path('revoke-orphan', token)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return result

    @task
    def revoke_prefix(self, prefix):
        """Revokes all tokens generated at a given prefix, along with child
        tokens, and all secrets generated using those tokens. Uses include
        revoking all tokens generated by a credential backend during a
        suspected compromise.

        Parameters:
            token (str): The token ID
        """
        method = 'POST'
        path = self.path('revoke-prefix', prefix)

        response = yield from self.req_handler(method, path)
        return ok(response)

    @task
    def renew(self, token, increment=None):
        """Renews a lease associated with a token.

        This is used to prevent the expiration of a token, and the automatic
        revocation of it.

        Parameters:
            token (str): The token ID
            increment (int): An optional requested lease increment can be
                             provided. This increment may be ignored.
        Returns:
            LoginToken: The client token
        """
        token = extract_id(token)
        method = 'POST'
        path = self.path('renew', token)
        data = {'increment': increment}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return LoginToken(**result)
