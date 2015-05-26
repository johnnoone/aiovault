"""
    secret.backends
    ~~~~~~~~~~~~~~~

"""

from .aws import AWSBackend
from .consul import ConsulBackend
from .generic import GenericBackend
from .mysql import MySQLBackend
from .postgresql import PostgreSQLBackend
from .transit import TransitBackend
from stevedore import driver

__all__ = ['AWSBackend', 'ConsulBackend', 'PostgreSQLBackend',
           'MySQLBackend', 'TransitBackend', 'GenericBackend',
           'load_backend']


def load_backend(type, backend):
    """Load secret backend.

    Parameters:
        type (str): The backend type
        backend (str): The backend init variables
    """
    mgr = driver.DriverManager(
        namespace='aiovault.secret.backend',
        name=type,
        invoke_on_load=True,
        invoke_kwds=backend
    )
    return mgr.driver
