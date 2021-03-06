from collections.abc import MutableMapping
from aiovault.util import convert_duration


class Status:

    def __init__(self, *, initialized):
        self.initialized = initialized

    def __repr__(self):
        return '<Status(initialized=%r)>' % self.initialized


class Initial:
    """
    Implements master initiales.

    Attributes:
        root_token (str): The root token
        keys (tuple): The secret keys
    """

    def __init__(self, *, root_token, keys):
        self.root_token = root_token
        self.keys = tuple(keys)

    def __iter__(self):
        for key in self.keys:
            yield key

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
        if 'policies' in data:
            value = data['policies']
            self.data['policies'] = set(value.split(',') if value else [])
        if 'lease' in data:
            value = data['lease']
            self.data['lease'] = convert_duration(value)

    def __eq__(self, other):
        if isinstance(other, Value):
            other == other.data
        return self.data == other

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
