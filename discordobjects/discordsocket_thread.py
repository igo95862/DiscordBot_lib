import asyncio
import logging
import typing
from concurrent.futures import Future as ConcurrentFuture, wait as concurrent_wait, ThreadPoolExecutor
from weakref import finalize

from . import discordsocketnew as discordsocket
from .constants import SocketEventNames
from .util import QueueDispenser


def dummy_plug(payload: dict):
    pass


class DiscordSocketThread:

    def __init__(self, token: str):
        self.local_event_loop = asyncio.get_event_loop()

        self.discord_socket_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.discord_socket = discordsocket.DiscordSocket(token, event_loop=self.discord_socket_loop,
                                                          event_handler=dummy_plug)

        self.thread = ThreadPoolExecutor(max_workers=1)
        self.thread_future = self.thread.submit(self.discord_socket_loop.run_forever)

        self.discord_socket_future = asyncio.run_coroutine_threadsafe(
            self.discord_socket.init(),
            self.discord_socket_loop)

        self.discord_socket_future.add_done_callback(self._socket_future_complete)

        self.event_dispatcher = QueueDispenser([x for x in SocketEventNames])
        self.event_dispatcher_running = False

        finalize(self, self.stop)

    def _socket_future_complete(self, finished_future: ConcurrentFuture):
        if self.discord_socket_future.cancelled():
            logging.info(f"Socket was canceled")
            return

        exception: BaseException = finished_future.exception()
        if exception is not None:
            logging.exception(f"Socket raised exception {repr(exception)} in thread container {repr(self)}")
        else:
            logging.warning(f"Socket unexpectedly closed in thread container {repr(self)}")

        self.discord_socket_future = asyncio.run_coroutine_threadsafe(
            self.discord_socket.init(),
            self.discord_socket_loop)
        self.discord_socket_future.add_done_callback(self._socket_future_complete)

    def event_queue_add_multiple(self, queue: asyncio.Queue, event_names_tuple: typing.Tuple[str, ...]) -> None:
        if not self.event_dispatcher_running:
            self.start_event_hook()
            self.event_dispatcher_running = True

        self.event_dispatcher.queue_add_multiple_slots(queue, event_names_tuple)

    def event_queue_add_single(self, queue: asyncio.Queue, event_name: str):
        if not self.event_dispatcher_running:
            self.start_event_hook()
            self.event_dispatcher_running = True

        self.event_dispatcher.queue_add_single_slot(queue, event_name)

    def start_event_hook(self) -> None:
        def event_hook(payload: dict):
            if payload['op'] == 0:
                asyncio.run_coroutine_threadsafe(self.event_dispatcher.event_put(payload['t'], payload['d']),
                                                 loop=self.local_event_loop)

        place_hook = asyncio.run_coroutine_threadsafe(self.discord_socket.set_event_handler(event_hook),
                                                      loop=self.discord_socket_loop)
        place_hook.result(timeout=10)

    def stop_event_hook(self) -> None:
        remove_hook = asyncio.run_coroutine_threadsafe(self.discord_socket.set_event_handler(dummy_plug),
                                                       loop=self.discord_socket_loop)
        remove_hook.result(timeout=10)

    def stop(self):
        self.discord_socket_future.cancel()
        concurrent_wait((self.discord_socket_future,))

        def stop_loop():
            self.discord_socket_loop.stop()

        self.discord_socket_loop.call_soon_threadsafe(stop_loop)
        concurrent_wait((self.thread_future,))
        self.thread.shutdown()
