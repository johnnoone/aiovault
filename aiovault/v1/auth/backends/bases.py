from abc import ABCMeta, abstractmethod
from aiovault.util import task


class AuthBackend(metaclass=ABCMeta):

    def __init__(self, name, type, req_handler):
        self.name = name
        self.type = type
        self.req_handler = req_handler

    @task
    @abstractmethod
    def login(self):
        """Performs login
        """

    @task
    def enable(self, description=None):
        """Enable backend

        Parameters:
            description (str): A human-friendly description of the auth backend
        Returns:
            bool
        """
        method = 'POST'
        path = '/sys/auth/%s' % self.name
        data = {'type': self.type,
                'description': description}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def disable(self):
        """Disable backend

        Returns:
            bool
        """
        method = 'DELETE'
        path = '/sys/auth/%s' % self.name

        response = yield from self.req_handler(method, path)
        return response.status == 204

    def __repr__(self):
        return '<%s(name=%r)>' % (self.__class__.__name__, self.name)
