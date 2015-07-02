"""
    auth.backends
    ~~~~~~~~~~~~~

"""

from .app_id import AppIDBackend
from .cert import CertBackend
from .github import GitHubBackend
from .ldap import LDAPBackend
from .userpass import UserPassBackend
from stevedore import DriverManager

__all__ = ['AppIDBackend', 'CertBackend', 'GitHubBackend',
           'LDAPBackend', 'UserPassBackend']


def load_backend(type, backend):
    """Load secret backend.

    Parameters:
        type (str): The backend type
        backend (str): The backend init variables
    """
    mgr = DriverManager(
        namespace='aiovault.auth.backend',
        name=type,
        invoke_on_load=True,
        invoke_kwds=backend
    )
    return mgr.driver
