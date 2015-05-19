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

    def __repr__(self):
        return '<%s(name=%r)>' % (self.__class__.__name__, self.name)
