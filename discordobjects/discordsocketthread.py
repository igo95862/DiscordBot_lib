from . import discordsocket
import asyncio
import threading
from functools import partial as func_partial
import typing

class DiscordSocketThread:

    def __init__(self, token: str = None, discord_socket: discordsocket.DiscordSocket = None,
                 shard_total: int = 1, shard_num: int = 0):

        if token is not None:
            # NOTE: check that the string has proper length and etc.?
            self.discord_socket_loop = asyncio.new_event_loop()
            self.discord_socket = discordsocket.DiscordSocket(token, shard_total=shard_total, shard_num=shard_num,
                                                              event_loop=self.discord_socket_loop)
        elif discord_socket is not None:
            self.discord_socket = discord_socket
            self.discord_socket.event_loop = self.discord_socket_loop
        else:
            raise TypeError('Neither token nor socket was passed to socket.')

        self.queue_to_hook_dict = {}

        self.discord_socket_loop.create_task(self.discord_socket.init())

        self.local_loop = asyncio.get_event_loop()

        # TODO: Timeout on queues as they can lock the application

        self.thread = threading.Thread(target=self.discord_socket_loop.run_forever)
        self.thread.start()

        '''
        ready_queue = asyncio.Queue(maxsize=1, loop=local_loop)
        
        self.queue_register(ready_queue, lambda x: x['t'] == 'READY')

        guild_create_queue = asyncio.Queue(loop=local_loop)
        self.queue_register(guild_create_queue, lambda x: x['t'] == 'GUILD_CREATE')

        

        self.ready_payload = local_loop.run_until_complete(ready_queue.get())
        self.queue_unregister(ready_queue)

        self.guild_init_payloads = []
        for i in range(len(self.ready_payload['d']['guilds'])):
            self.guild_init_payloads.append(local_loop.run_until_complete(guild_create_queue.get()))

        self.queue_unregister(guild_create_queue)
        '''

        # Event queues
        self.main_queue = None
        self.main_event_hook = None
        self.listeners_count = 0
        self.listeners = {}
        self.event_dispatcher_task = None

    def request_guild_members(self, guild_id: str, query: str = '', limit: int = 0):
        return asyncio.run_coroutine_threadsafe(
            self.discord_socket.request_guild_members(
                guild_id, query, limit),
            self.discord_socket_loop)

    def status_update(self, status_type: str, is_afk: bool,
                      game: dict = None, since_time_seconds: int = None):
        return asyncio.run_coroutine_threadsafe(
            self.discord_socket.status_update(
                status_type, is_afk, game, since_time_seconds),
            self.discord_socket_loop)

    def voice_state_update(self, guild_id: str, channel_id: int = None,
                           mute_self: bool = None, deaf_self: bool = False):
        return asyncio.run_coroutine_threadsafe(
            self.discord_socket.voice_state_update(
                guild_id, channel_id, mute_self, deaf_self),
            self.discord_socket_loop)


    # region Events
    def _main_queue_create(self) -> None:
        self.main_queue = asyncio.Queue()

        async def main_event_hook(payload: dict):
                asyncio.run_coroutine_threadsafe(self.main_queue.put(payload), loop=self.local_loop)

        self.main_event_hook = main_event_hook
        self.discord_socket_loop.call_soon_threadsafe(func_partial
                                                      (self.discord_socket.event_hooks.append, self.main_event_hook))
        self.event_dispatcher_task = self.local_loop.create_task(self.event_dispatcher())

    def _main_queue_delete(self) -> None:
        self.event_dispatcher_task.cancel()
        self.discord_socket_loop.call_soon_threadsafe(func_partial(
            self.discord_socket.event_hooks.remove, self.main_event_hook))
        self.main_queue = None

    async def event_dispatcher(self) -> None:
        while True:
            payload = await self.main_queue.get()
            for l in self.listeners.values():
                asyncio.ensure_future(l(payload['t'], payload['d']), loop=self.local_loop)

    def event_queue_create(self, event_name_qualifier: str = '') -> 'DiscordEventQueue':
        if self.listeners_count == 0:
            self._main_queue_create()

        return self.DiscordEventQueue(self, event_name_qualifier)

    class DiscordEventQueue(asyncio.Queue):

        def __init__(self, parent: 'DiscordSocketThread', event_name: str):
            super().__init__(loop=parent.local_loop)
            self.parent = parent
            self.event_name = event_name

        def __enter__(self) -> None:
            async def queue_hook(event_name: str, event_data: dict):
                if event_name == self.event_name:
                    await self.put(event_data)
            self.parent.listeners[self] = queue_hook
            self.parent.listeners_count += 1

        def __exit__(self, exception_type, exception_value, traceback) -> None:
            self.parent.listeners.pop(self)
            self.parent.listeners_count -= 1
            if self.parent.listeners_count == 0:
                self.parent._main_queue_delete()

    def event_event_create(self, condition_func: typing.Callable, event_name: str):
        if self.listeners_count == 0:
            self._main_queue_create()

        return self.DiscordEventEvent(self, condition_func, event_name)

    class DiscordEventEvent(asyncio.Event):

        def __init__(self, parent: 'DiscordSocketThread', condition_func: typing.Callable, event_name: str):
            super().__init__()
            self.parent = parent
            self.event_name = event_name
            self.condition_func = condition_func

        async def __call__(self) -> None:
            async def event_hook(event_name: str, event_data: dict):
                if event_name == self.event_name:
                    try:
                        if self.condition_func(event_data):
                            self.set()
                    except KeyError:
                        pass

            self.parent.listeners[self] = event_hook
            self.parent.listeners_count += 1
            await self.wait()
            self.parent.listeners.pop(self)
            self.parent.listeners_count -= 1
            if self.parent.listeners_count == 0:
                self.parent._main_queue_delete()

    # endregion

