from abc import ABCMeta, abstractmethod


class AuditBackend(metaclass=ABCMeta):

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @abstractmethod
    def validate(self, **kwargs):
        """Validate audit options
        """
