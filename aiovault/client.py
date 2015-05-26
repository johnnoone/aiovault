from . import v1
from .request import Request
from .util import task


class Vault(v1.SysEndpoint):

    def __init__(self, addr, token=None):
        token = getattr(token, 'id', token)
        self.req_handler = Request(addr, 'v1', token=token)

    @property
    def audit(self):
        return v1.AuditEndpoint(self.req_handler)

    @property
    def auth(self):
        return v1.AuthEndpoint(self.req_handler)

    @property
    def lease(self):
        return v1.LeaseEndpoint(self.req_handler)

    @property
    def policy(self):
        return v1.PolicyEndpoint(self.req_handler)

    @property
    def raw(self):
        return v1.RawEndpoint(self.req_handler)

    @property
    def seal(self):
        return v1.SealEndpoint(self.req_handler)

    @property
    def secret(self):
        return v1.SecretEndpoint(self.req_handler)

    @task
    def read(self, path, **kwargs):
        method = kwargs.pop('method', 'GET')
        response = yield from self.req_handler(method, path, **kwargs)
        return response

    @task
    def write(self, path, **kwargs):
        method = kwargs.pop('method', 'POST')
        response = yield from self.req_handler(method, path, **kwargs)
        return response

    @task
    def delete(self, path, **kwargs):
        method = kwargs.pop('method', 'DELETE')
        response = yield from self.req_handler(method, path, **kwargs)
        return response

    def __repr__(self):
        return '<Vault(addr=%r)>' % self.req_handler.addr
