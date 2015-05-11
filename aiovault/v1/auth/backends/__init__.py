from .app_id import AppIDBackend
from .cert import CertBackend
from .github import GitHubBackend
from .token import TokenBackend
from .userpass import UserPassBackend
from stevedore import driver

__all__ = ['AppIDBackend', 'CertBackend', 'GitHubBackend',
           'TokenBackend', 'UserPassBackend']


def load_backend(type, name, *args, **kwargs):
    """Load secret backend.

    Parameters:
        type (str): The backend type
        name (str): The backend name
    """
    kwargs.setdefault('name', name)
    mgr = driver.DriverManager(
        namespace='aiovault.auth.backend',
        name=type,
        invoke_on_load=True,
        invoke_args=args,
        invoke_kwds=kwargs
    )
    return mgr.driver
