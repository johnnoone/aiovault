import asyncio
from abc import ABCMeta, abstractmethod
from aiovault.exceptions import HTTPError, LoginError

__all__ = ['authenticate', 'LoginToken', 'ReadToken']


@asyncio.coroutine
def authenticate(req_handler, *args, **kwargs):
    try:
        response = yield from req_handler(*args, **kwargs)
        result = yield from response.json()
        return LoginToken(**result)
    except HTTPError as error:
        raise LoginError(errors=error.errors)


class Token(metaclass=ABCMeta):

    @property
    @abstractmethod
    def id(self):
        """Returns token id"""


class ReadToken(Token):
    """
    Vault response is like this one:

    .. code-block:: javascript

        {
          "auth": null,
          "data": {
            "display_name": "token",
            "id": "95aeacef-5e5a-e436-96f7-4c9a9837f36a",
            "meta": null,
            "num_uses": 0,
            "path": "auth/token/create",
            "policies": ["root"]
          },
          "lease_duration": 0,
          "lease_id": "",
          "renewable": false
        }

    """
    def __init__(self, *, auth, renewable, data, lease_duration, lease_id):
        self.auth = auth
        self.renewable = renewable
        self.data = data
        self.lease_duration = lease_duration
        self.lease_id = lease_id

    @property
    def id(self):
        """Returns token id"""
        return self.data['id']

    def __eq__(self, other):
        if isinstance(other, ReadToken):
            other == other.data
        return self.data == other

    def __getitem__(self, name):
        return self.data[name]

    def __iter__(self):
        return iter(self.data.keys())

    def __repr__(self):
        return '<Token(id=%r)>' % self.data['id']


class LoginToken(Token):
    """
    Vault response is like this one:

    .. code-block:: javascript

        {
          "auth": {
            "client_token": "95aeacef-5e5a-e436-96f7-4c9a9837f36a",
            "lease_duration": 0,
            "metadata": null,
            "policies": ["root"],
            "renewable": false
          },
          "data": null,
          "lease_duration": 0,
          "lease_id": "",
          "renewable": false
        }
    """

    def __init__(self, *, auth, data, lease_duration, lease_id, renewable):
        self.renewable = renewable
        self.lease_id = lease_id
        self.lease_duration = lease_duration
        self.data = data
        self.auth = auth

    @property
    def id(self):
        """Returns token id"""
        return self.auth['client_token']

    def __eq__(self, other):
        if isinstance(other, LoginToken):
            other == other.auth
        return self.auth == other

    def __getitem__(self, name):
        return self.auth[name]

    def __iter__(self):
        return iter(self.auth.keys())

    def __repr__(self):
        return '<LoginToken(id=%r)>' % self.auth['client_token']
