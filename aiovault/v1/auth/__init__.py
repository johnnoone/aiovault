"""
    auth
    ~~~~

"""

from .backends import load_backend
from collections.abc import Mapping
from aiovault.exceptions import InvalidPath
from aiovault.token import ReadToken, LoginToken
from aiovault.util import extract_name, extract_id
from aiovault.util import ok, task, Path, format_duration

__all__ = ['authenticate', 'AuthEndpoint', 'AuthCollection']


class AuthEndpoint:

    def __init__(self, req_handler):
        self.req_handler = req_handler

    @property
    def path(self):
        return Path('/sys/auth')

    @property
    def token_path(self):
        return Path('/auth/token')

    @task
    def items(self):
        """Lists all the enabled auth backends

        Returns:
            AuthCollection
        """
        method = 'GET'
        path = self.path

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return AuthCollection(result, self.req_handler)

    def load(self, name, *, type=None):
        """Returns auth backend

        Parameters:
            name (str): The auth backend name
        Returns
            AuthBackend
        """
        type = type or getattr(name, 'type', name)
        name = extract_name(name)

        return load_backend(type, {
            'name': name,
            'type': type,
            'req_handler': self.req_handler
        })

    @task
    def login(self, name, *, type=None, **credentials):
        """Login

        Parameters:
            name (str): The name of mount
            type (str): The name of the auth backend type, such as ``github``
            credentials (str): Login credentials
        Returns
            AuthBackend
        """
        backend = self.load(name, type=type)
        try:
            token = yield from backend.login(**credentials)
            return token
        except AttributeError:
            return NotImplemented

    @task
    def enable(self, name, *, type=None, description=None):
        """Enable and load a new auth backend

        Parameters:
            name (str): The name of mount
            type (str): The name of the auth backend type, such as ``github``
            description (str): A human-friendly description of the auth backend
        Returns
            AuthBackend
        """
        backend = self.load(name, type=type)
        enabled = yield from backend.enable(description)
        if enabled:
            return backend

    @task
    def disable(self, name):
        """Disable the auth backend at the given mount point

        Parameters:
            name (str): The name of mount
        """
        method = 'DELETE'
        path = self.path(name)

        response = yield from self.req_handler(method, path)
        return ok(response)

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
                            token. Defaults to no limit.
        Returns:
            LoginToken: The client token
        """
        method = 'POST'
        path = self.token_path('create')
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
        path = self.token_path('lookup-self')

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
        path = self.token_path('lookup', token)

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
        path = self.token_path('revoke', token)

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
        path = self.token_path('revoke-orphan', token)

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
        path = self.token_path('revoke-prefix', prefix)

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
        path = self.token_path('renew', token)
        data = {'increment': increment}

        response = yield from self.req_handler(method, path, json=data)
        result = yield from response.json()
        return LoginToken(**result)


class AuthCollection(Mapping):

    def __init__(self, backends, req_handler):
        self.backends = backends
        self.req_handler = req_handler

    def __getitem__(self, name):
        path = '%s/' % name
        return load_backend(self.backends[path]['type'], {
            'name': name,
            'type': self.backends[path]['type'],
            'req_handler': self.req_handler
        })

    def __iter__(self):
        for key in self.backends.keys():
            yield key[:-1]

    def __len__(self):
        return len(self.backends)

    def __repr__(self):
        data = tuple(self.backends.keys())
        return '<AuthCollection{!r}>'.format(data)
