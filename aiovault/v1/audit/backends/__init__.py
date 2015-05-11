from .file import FileBackend
from .syslog import SyslogBackend
from stevedore import driver

__all__ = ['FileBackend', 'SyslogBackend', 'load_backend']


def load_backend(type, name, *args, **kwargs):
    """Load audit backend.

    Parameters:
        type (str): The backend type
        name (str): The backend name
    """
    kwargs.setdefault('name', name)
    mgr = driver.DriverManager(
        namespace='aiovault.audit.backend',
        name=type,
        invoke_on_load=True,
        invoke_args=args,
        invoke_kwds=kwargs
    )
    return mgr.driver
