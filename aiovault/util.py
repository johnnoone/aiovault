import asyncio
import inspect
from base64 import b64decode, b64encode
from datetime import timedelta
from functools import partial, wraps

__all__ = ['format_duration', 'format_policies', 'task']


def base64_decode(data):
    """Decode a Base64 encodedstring"""
    return b64decode(data.encode('utf-8')).decode('utf-8')


def base64_encode(data):
    """Encode a string using Base64"""
    return b64encode(data.encode('utf-8')).decode('utf-8')


def format_duration(obj):
    """Converts obj to consul duration"""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int):
        return '%ss' % obj
    if isinstance(obj, timedelta):
        return '%ss' % int(obj.total_seconds())
    raise ValueError('wrong type %r' % obj)


def format_policies(obj):
    if isinstance(obj, (list, set, tuple)):
        obj = ','.join(str(element) for element in obj)
    elif obj:
        obj = str(obj)
    return obj


def task(func=None, *, loop=None):
    """Transforms func into an asyncio task."""

    if not func:
        if not loop:
            raise ValueError('loop is required')
        return partial(task, loop=loop)

    if getattr(func, '_is_task', False):
        return func

    coro = asyncio.coroutine(func)

    if inspect.ismethod(func):
        @wraps(func)
        def wrapper(self, *arg, **kwargs):
            l = loop or self.loop
            return asyncio.async(coro(self, *arg, **kwargs), loop=l)
    else:
        @wraps(func)
        def wrapper(*arg, **kwargs):
            return asyncio.async(coro(*arg, **kwargs), loop=loop)
    wrapper._is_task = True
    return wrapper


def mark_task(func):
    """Mark function as a defacto task (for documenting purpose)"""
    func._is_task = True
    return func


class lazy_property:
    """
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__
        self.__name__ = fget.__name__
        self.__doc__ = fget.__doc__

    def __get__(self, obj, cls):
        if obj:
            value = self.fget(obj)
            setattr(obj, self.func_name, value)
            return value
        return self

try:
    # python >= 3.4
    from contextlib import suppress
except ImportError:

    class suppress:
        """Context manager to suppress specified exceptions

        After the exception is suppressed, execution proceeds with the next
        statement following the with statement.

             with suppress(FileNotFoundError):
                 os.remove(somefile)
             # Execution still resumes here if the file was already removed
        """

        def __init__(self, *exceptions):
            self._exceptions = exceptions

        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            # Unlike isinstance and issubclass, CPython exception handling
            # currently only looks at the concrete type hierarchy (ignoring
            # the instance and subclass checking hooks). While Guido considers
            # that a bug rather than a feature, it's a fairly hard one to fix
            # due to various internal implementation details. suppress provides
            # the simpler issubclass based semantics, rather than trying to
            # exactly reproduce the limitations of the CPython interpreter.
            #
            # See http://bugs.python.org/issue12029 for more details
            return exctype is not None and issubclass(exctype, self._exceptions)  # noqa
