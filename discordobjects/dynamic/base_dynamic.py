import asyncio
import typing
import logging

from ..util import QueueDispenser
from ..client import DiscordClientAsync


class BaseDynamic:

    def __init__(
            self, client_bind: DiscordClientAsync, queue_dispencer_slots: typing.Iterable[typing.Hashable],
            event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
            start_immediately: bool = True):
        self.client_bind = client_bind
        self.event_loop = event_loop
        self.auto_update_task: asyncio.Task = None
        self.await_init: asyncio.Future = asyncio.Future(loop=self.event_loop)
        self.queue_dispenser = QueueDispenser(queue_dispencer_slots)
        if start_immediately:
            self.start_auto_task()

    def start_auto_task(self):
        if self.auto_update_task is not None:
            self.auto_update_task.cancel()
            self.await_init = asyncio.Future()
        self.auto_update_task: asyncio.Task = self.event_loop.create_task(self._auto_update())
        self.auto_update_task.add_done_callback(self._log_auto_update_failure)

    def _log_auto_update_failure(self, fut: asyncio.Future):
        logging.error(f"Dynamic object auto_update of class {self.__class__.__name__} failed: {fut}")

    def __await__(self) -> typing.Awaitable[bool]:
        if self.auto_update_task is None:
            self.start_auto_task()
        return self.await_init.__await__()

    async def _auto_update(self):
        raise NotImplementedError
