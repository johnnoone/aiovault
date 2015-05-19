import asyncio
import json
import logging
import ssl
from .exceptions import DownError, HTTPError, InvalidRequest, InvalidPath
from .exceptions import InternalServerError, RateLimitExceeded, Unauthorized
from aiohttp import ClientSession, TCPConnector


class Request:

    def __init__(self, addr, version, token=None, cert=None):
        self.addr = addr
        self.version = version
        self.token = token

        cookies = {}
        if self.token:
            cookies.setdefault('token', self.token)

        connector = None
        if cert:
            logging.info('use ssl context')
            if addr.startswith('http://'):
                n = 'https://%s' % addr[7:]
                logging.warn('exchanged %r to %r', addr, n)
                self.addr = n

            certfile, keyfile = cert
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(certfile, keyfile)
            connector = TCPConnector(verify_ssl=True, ssl_context=context)

        self.session = ClientSession(cookies=cookies, connector=connector)

    @asyncio.coroutine
    def request(self, method, path, **kwargs):
        url = '%s/%s%s' % (self.addr, self.version, path)

        for field in ('params', 'data', 'json'):
            if field in kwargs and isinstance(kwargs[field], dict):
                kwargs[field] = no_null(kwargs[field])

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


def no_null(data):
    return {k: v for k, v in data.items() if v is not None}
