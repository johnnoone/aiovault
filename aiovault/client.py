import asyncio
import json
from aiohttp import ClientSession
from . import v1
from .exceptions import DownError, HTTPError, InvalidRequest, InvalidPath
from .exceptions import InternalServerError, RateLimitExceeded, Unauthorized


class Vault(v1.SysEndpoint):

    def __init__(self, addr, token=None):
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

    def __repr__(self):
        return '<Vault(addr=%r)>' % self.req_handler.addr


class Request:

    def __init__(self, addr, version, token=None):
        self.addr = addr
        self.version = version
        self.token = token

        cookies = {}
        if self.token:
            cookies.setdefault('token', self.token)
        self.session = ClientSession(cookies=cookies)

    @asyncio.coroutine
    def request(self, method, path, **kwargs):
        url = '%s/%s%s' % (self.addr, self.version, path)

        data = kwargs.pop('json', None)
        if data is not None:
            kwargs['data'] = json.dumps(data)
            headers = kwargs.setdefault('headers', {})
            headers['Content-Type'] = 'application/json'

        response = yield from self.session.request(method, url, **kwargs)

        if response.status in (200, 204):
            return response
        data = yield from response.json()
        if response.status == 400:
            raise InvalidRequest(data)
        if response.status == 401:
            raise Unauthorized(data)
        if response.status == 404:
            raise InvalidPath(data)
        if response.status == 429:
            raise RateLimitExceeded(data)
        if response.status == 500:
            raise InternalServerError(data)
        if response.status == 503:
            raise DownError(data)
        raise HTTPError(data)

    __call__ = request
