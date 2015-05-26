from abc import ABCMeta, abstractmethod
from collections.abc import MutableMapping


class Status:

    def __init__(self, *, initialized):
        self.initialized = initialized

    def __repr__(self):
        return '<Status(initialized=%r)>' % self.initialized


class Initial:

    def __init__(self, *, root_token, keys):
        self.root_token = root_token
        self.keys = keys

    def __repr__(self):
        return '<Initial(root_token=%r, keys=%r)>' % (
            self.root_token, self.keys)


class HighAvailibility:

    def __init__(self, *, ha_enabled, is_self, leader_address):
        self.enabled = ha_enabled
        self.is_self = is_self
        self.leader_address = leader_address

    def __repr__(self):
        if self.enabled:
            return '<HighAvailibility(is_self=%r, leader_address=%r)>' % (
                self.is_self, self.leader_address)
        else:
            return '<HighAvailibility(ha_enabled=%r)>' % self.enabled


class Health:

    def __init__(self, *, initialized, sealed, standby):
        self.initialized = initialized
        self.sealed = sealed
        self.standby = standby

    def __repr__(self):
        return '<Health(initialized=%r, sealed=%r, standby=%r)>' % (
            self.initialized, self.sealed, self.standby)


class SealStatus:

    def __init__(self, sealed, t, n, progress):
        self.sealed = sealed
        self.threshold = t
        self.shares = n
        self.progress = progress

    def __repr__(self):
        return '<SealStatus(sealed=%r, threshold=%r, shares=%r, progress=%r)>' % (  # noqa
            self.sealed, self.threshold, self.shares, self.progress)


class Value(MutableMapping):

    def __init__(self, *, lease_duration, auth, renewable, lease_id, data):
        self.lease_duration = lease_duration
        self.auth = auth
        self.renewable = renewable
        self.lease_id = lease_id
        self.data = data

    def __eq__(self, other):
        if isinstance(other, Value):
            other == other.data
        return self.data == other

    def __hasitem__(self, name):
        return self.data[name]

    def __getitem__(self, name):
        return self.data[name]

    def __setitem__(self, name, value):
        self.data[name] = value

    def __delitem__(self, name):
        del self.data[name]

    def __iter__(self):
        return iter(self.data.keys())

    def __len__(self):
        return len(self.data.keys())

    def __repr__(self):
        return '<Value(data=%r)>' % self.data


class Policy:

    def __init__(self, *, name, rules):
        self.name = name
        self.rules = rules or {}

    def __eq__(self, other):
        if isinstance(other, Policy):
            other == other.rules
        return self.rules == other

    def __repr__(self):
        return '<Policy(name=%r)>' % self.name


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


class WrittenToken(Token):
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
        if isinstance(other, WrittenToken):
            other == other.auth
        return self.auth == other

    def __getitem__(self, name):
        return self.auth[name]

    def __iter__(self):
        return iter(self.auth.keys())

    def __repr__(self):
        return '<WrittenToken(id=%r)>' % self.auth['client_token']
