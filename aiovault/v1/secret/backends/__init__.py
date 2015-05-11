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


def load_backend(type, name, *args, **kwargs):
    """Load secret backend.

    Parameters:
        type (str): The backend type
        name (str): The backend name
    """
    kwargs.setdefault('name', name)
    mgr = driver.DriverManager(
        namespace='aiovault.secret.backend',
        name=type,
        invoke_on_load=True,
        invoke_args=args,
        invoke_kwds=kwargs
    )
    return mgr.driver
