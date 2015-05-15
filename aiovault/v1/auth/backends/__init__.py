import asyncio
import logging
from .app_id import AppIDBackend
from .cert import CertBackend
from .github import GitHubBackend
from .token import TokenBackend
from .userpass import UserPassBackend
from inspect import signature
from stevedore import DriverManager, ExtensionManager
from aiovault.exceptions import InvalidRequest, LoginError

__all__ = ['AppIDBackend', 'CertBackend', 'GitHubBackend',
           'TokenBackend', 'UserPassBackend']


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


def load_login(type, backend, credentials):
    """Try to log with any backend.

    Parameters:
        type (str): The backend type
        backend (dict): The backend init variables
        credentials (dict): The login variables
    """

    tasks = []

    def ask(ext, credentials):
        try:
            sign = signature(ext.obj.login)
            sign.bind(**credentials)
        except TypeError:
            logging.info('wrong params for %s', ext.obj.__class__.__name__)
        except AttributeError:
            logging.info('no login form for %s', ext.obj.__class__.__name__)
        else:
            logging.info('use %s', ext.obj.__class__.__name__)
            task = ext.obj.login(**credentials)
            tasks.append(task)

    mgr = ExtensionManager(
        namespace='aiovault.auth.backend',
        invoke_on_load=True,
        invoke_kwds=backend,
        propagate_map_exceptions=True
    )

    mgr.map(ask, credentials)
    if not tasks:
        raise Exception('No backend found, maybe a credential mismatch?')
    done, pending = yield from asyncio.wait(tasks)

    reasons = []

    for future in done:
        try:
            result = future.result()
            if result:
                return result
        except InvalidRequest as error:
            reasons.extend(error.errors)
        except Exception as err:
            logging.warn(err)

    raise LoginError('Unable to login with these credentials',
                     credentials=credentials,
                     errors=reasons)
