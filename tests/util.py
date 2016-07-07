import functools
from unittest import mock as um

from tornado import ioloop as ti, gen as tg


class AsyncMock(um.Mock):

    def __init__(self, return_value=None):
        super(AsyncMock, self).__init__(return_value=self)

        self._return_value = return_value
        self._awaited = False

    def __await__(self):
        yield tg.moment
        self._awaited = True
        return self._return_value

    def assert_awaited(self):
        assert self._awaited


def async_call(fn, *args, **kwargs):
    return ti.IOLoop.instance().run_sync(functools.partial(fn, *args, **kwargs))