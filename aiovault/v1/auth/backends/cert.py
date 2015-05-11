import asyncio
from .bases import AuthBackend


class CertBackend(AuthBackend):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @asyncio.coroutine
    def login(self):
        method = 'POST'
        path = '/auth/%s/certs/login' % self.name

    @asyncio.coroutine
    def set_cert(self, name, display_name, policies, certificate, lease):
        """docstring for configure

        Parameters:
            team (str):
            policies (str):
        """
        method = 'POST'
        path = '/auth/%s/certs/%s' % (self.name, name)
        data = {'policies': policies,
                'display_name': display_name,
                'policies': policies,
                'certificate': certificate,
                'lease': lease}

        response = yield from self.req_handler(method, path, data=data)
        result = yield from response.json()
        return result
