import asyncio
import logging
import typing
from concurrent.futures import Future as ConcurrentFuture, wait as concurrent_wait, ThreadPoolExecutor
from weakref import finalize

from . import discordsocketnew as discordsocket
from .constants import SocketEventNames
from .util import QueueDispenser, EventDispenser


def dummy_plug(payload: dict):
    pass


class DiscordSocketThread:

    def __init__(self, token: str):
        self.local_event_loop = asyncio.get_event_loop()
        self.token = token

        self.discord_socket_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.discord_socket = discordsocket.DiscordSocket(
            token, event_loop=self.discord_socket_loop, event_handler=dummy_plug)

        self.thread = ThreadPoolExecutor(max_workers=1)
        self.thread_future = self.thread.submit(self.discord_socket_loop.run_forever)

        self.discord_socket_future = asyncio.run_coroutine_threadsafe(
            self.discord_socket.init(),
            self.discord_socket_loop)

        self.discord_socket_future.add_done_callback(self._socket_future_complete)

        self.event_dispatcher = QueueDispenser([x for x in SocketEventNames])
        self.event_dispatcher_running = False

        self.failure_count = 0
        self.session_id: str = None

        finalize(self, self.stop)

    def restart_socket(self):
        self.stop()
        self.discord_socket = discordsocket.DiscordSocket(
            self.token, event_loop=self.discord_socket_loop, event_handler=dummy_plug, session_id=self.session_id)

        self.discord_socket_future = asyncio.run_coroutine_threadsafe(
            self.discord_socket.init(),
            self.discord_socket_loop)

        self.discord_socket_future.add_done_callback(self._socket_future_complete)
        self.start_event_hook()

    def _socket_future_complete(self, finished_future: ConcurrentFuture):
        if self.discord_socket_future.cancelled():
            logging.info(f"Socket was canceled")
            return

        exception: BaseException = finished_future.exception()
        if exception is not None:
            logging.exception(f"Socket raised exception {repr(exception)} in thread container {repr(self)}")
        else:
            logging.warning(f"Socket unexpectedly closed in thread container {repr(self)}")

        self.failure_count += 1
        if self.failure_count == 3:
            logging.critical(f"Failed to reinitialize socket {self.failure_count}. Shutting down.")
            self.session_id = self.discord_socket.session_id
            self.restart()
            return

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

    def restart(self):
        pass


class SocketThread:

    def __init__(self, token: str):
        self.local_event_loop = asyncio.get_event_loop()

        self.discord_socket_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.discord_socket = discordsocket.DiscordSocket(
            token, event_loop=self.discord_socket_loop, event_handler=dummy_plug)

        self.thread = ThreadPoolExecutor(max_workers=1)
        self.thread_future = self.thread.submit(self.discord_socket_loop.run_forever)

        self.discord_socket_future = asyncio.run_coroutine_threadsafe(
            self.discord_socket.init(),
            self.discord_socket_loop)

        self.discord_socket_future.add_done_callback(self._socket_future_complete)

        self.failure_count = 0

        # Event Dispensers
        self.event_ready = EventDispenser(self.local_event_loop)
        self.event_resumed = EventDispenser(self.local_event_loop)

        self.event_channel_create = EventDispenser(self.local_event_loop)
        self.event_channel_update = EventDispenser(self.local_event_loop)
        self.event_channel_delete = EventDispenser(self.local_event_loop)
        self.event_channel_pins_update = EventDispenser(self.local_event_loop)

        self.event_guild_create = EventDispenser(self.local_event_loop)
        self.event_guild_update = EventDispenser(self.local_event_loop)
        self.event_guild_delete = EventDispenser(self.local_event_loop)

        self.event_guild_ban_add = EventDispenser(self.local_event_loop)
        self.event_guild_ban_remove = EventDispenser(self.local_event_loop)
        self.event_guild_emoji_update = EventDispenser(self.local_event_loop)
        self.event_guild_integrations_update = EventDispenser(self.local_event_loop)

        self.event_guild_member_add = EventDispenser(self.local_event_loop)
        self.event_guild_member_remove = EventDispenser(self.local_event_loop)
        self.event_guild_member_update = EventDispenser(self.local_event_loop)

        self.event_guild_role_create = EventDispenser(self.local_event_loop)
        self.event_guild_role_update = EventDispenser(self.local_event_loop)
        self.event_guild_role_delete = EventDispenser(self.local_event_loop)

        self.event_message_create = EventDispenser(self.local_event_loop)
        self.event_message_update = EventDispenser(self.local_event_loop)
        self.event_message_delete = EventDispenser(self.local_event_loop)
        self.event_message_delete_bulk = EventDispenser(self.local_event_loop)

        self.event_message_reaction_add = EventDispenser(self.local_event_loop)
        self.event_message_reaction_remove = EventDispenser(self.local_event_loop)
        self.event_message_reaction_remove_all = EventDispenser(self.local_event_loop)

        self.event_presence_update = EventDispenser(self.local_event_loop)
        self.event_typing_start = EventDispenser(self.local_event_loop)
        self.event_user_update = EventDispenser(self.local_event_loop)
        self.event_voice_state_update = EventDispenser(self.local_event_loop)
        self.event_voice_server_update = EventDispenser(self.local_event_loop)
        self.event_webhooks_update = EventDispenser(self.local_event_loop)

        self.event_map = {
            SocketEventNames.READY: self.event_ready,
            SocketEventNames.RESUMED: self.event_resumed,
            SocketEventNames.CHANNEL_CREATE: self.event_channel_create,
            SocketEventNames.CHANNEL_UPDATE: self.event_channel_update,
            SocketEventNames.CHANNEL_DELETE: self.event_channel_delete,
            SocketEventNames.CHANNEL_PINS_UPDATE: self.event_channel_pins_update,
            SocketEventNames.GUILD_CREATE: self.event_guild_create,
            SocketEventNames.GUILD_UPDATE: self.event_guild_update,
            SocketEventNames.GUILD_DELETE: self.event_guild_delete,
            SocketEventNames.GUILD_BAN_ADD: self.event_guild_ban_add,
            SocketEventNames.GUILD_BAN_REMOVE: self.event_guild_ban_remove,
            SocketEventNames.GUILD_EMOJIS_UPDATE: self.event_guild_emoji_update,
            SocketEventNames.GUILD_INTEGRATIONS_UPDATE: self.event_guild_integrations_update,
            SocketEventNames.GUILD_MEMBER_ADD: self.event_guild_member_add,
            SocketEventNames.GUILD_MEMBER_REMOVE: self.event_guild_member_remove,
            SocketEventNames.GUILD_MEMBER_UPDATE: self.event_guild_member_update,
            SocketEventNames.GUILD_ROLE_CREATE: self.event_guild_role_create,
            SocketEventNames.GUILD_ROLE_UPDATE: self.event_guild_role_update,
            SocketEventNames.GUILD_ROLE_DELETE: self.event_guild_role_delete,
            SocketEventNames.MESSAGE_CREATE: self.event_message_create,
            SocketEventNames.MESSAGE_UPDATE: self.event_message_update,
            SocketEventNames.MESSAGE_DELETE: self.event_message_delete,
            SocketEventNames.MESSAGE_DELETE_BULK: self.event_message_delete_bulk,
            SocketEventNames.MESSAGE_REACTION_ADD: self.event_message_reaction_add,
            SocketEventNames.MESSAGE_REACTION_REMOVE: self.event_message_reaction_remove,
            SocketEventNames.MESSAGE_REACTION_REMOVE_ALL: self.event_message_reaction_remove_all,
            SocketEventNames.PRESENCE_UPDATE: self.event_presence_update,
            SocketEventNames.TYPING_START: self.event_typing_start,
            SocketEventNames.USER_UPDATE: self.event_user_update,
            SocketEventNames.VOICE_STATE_UPDATE: self.event_voice_server_update,
            SocketEventNames.VOICE_SERVER_UPDATE: self.event_voice_server_update,
            SocketEventNames.WEBHOOKS_UPDATE: self.event_webhooks_update,
        }


    def _socket_future_complete(self, finished_future: ConcurrentFuture):
        if self.discord_socket_future.cancelled():
            logging.info(f"Socket was canceled")
            return

        exception: BaseException = finished_future.exception()
        if exception is not None:
            logging.exception(f"Socket raised exception {repr(exception)} in thread container {repr(self)}")
        else:
            logging.warning(f"Socket unexpectedly closed in thread container {repr(self)}")

        self.failure_count += 1
        if self.failure_count == 3:
            logging.critical(f"Failed to reinitialize socket {self.failure_count}. Shutting down.")
            return

        self.discord_socket_future = asyncio.run_coroutine_threadsafe(
            self.discord_socket.init(),
            self.discord_socket_loop)
        self.discord_socket_future.add_done_callback(self._socket_future_complete)