import asyncio
import inspect
from datetime import timedelta
from functools import partial, wraps

__all__ = ['format_duration', 'format_policies', 'task']


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
