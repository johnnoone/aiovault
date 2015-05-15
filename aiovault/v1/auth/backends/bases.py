import asyncio
from abc import ABCMeta, abstractmethod
from aiovault.util import task


class AuthBackend(metaclass=ABCMeta):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @task
    @abstractmethod
    def login(self):
        """Performs login
        """

    @asyncio.coroutine
    def help(self):
        """Returns help for this backend.

        .. note:: You must be logged with the good policies
        """
        method = 'GET'
        path = '/sys/auth/%s/' % self.name
        params = {'help': 1}

        response = yield from self.req_handler(method, path, params=params)
        result = yield from response.json()
        return result

    def __repr__(self):
        return '<%s(name=%r)>' % (self.__class__.__name__, self.name)
