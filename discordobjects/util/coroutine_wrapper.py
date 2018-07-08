from asyncio import iscoroutinefunction, AbstractEventLoop
from typing import Callable


def wrap_if_coroutine(event_loop: AbstractEventLoop, call: Callable) -> Callable:
    if iscoroutinefunction(call):
        def wrapper(*args, **kwargs):
            event_loop.create_task(call(*args, **kwargs))

        return wrapper
    else:
        return call
