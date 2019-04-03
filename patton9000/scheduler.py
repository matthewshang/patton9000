# Based on http://numberoverzero.com/posts/2017/07/17/periodic-execution-with-asyncio
import asyncio
import functools


def _schedule_func(func, args=None, kwargs=None, interval=60, *, loop):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    async def periodic_func():
        while True:
            await asyncio.sleep(interval, loop=loop)
            await func(*args, **kwargs)

    return loop.create_task(periodic_func())


def create_scheduler(loop):
    return functools.partial(_schedule_func, loop=loop)
