import websockets
import asyncio
import json
import zlib
import platform

identity_template = {
    'properties':
        {
            "$os": platform.system() + ' ' + platform.version() + ' ' + platform.machine(),
            "$device": platform.python_implementation() + ' ' + platform.python_version(),
            "$browser": "Discord Python Library"
        },
    'compress': True,
    "large_threshold": 250,
}


class DiscordSocket:
    def __init__(self, token,
                 socket_url='wss://gateway.discord.gg/?v=6&encoding=json',
                 presence={'status': 'online', 'afk': False}.copy(),
                 shard_num: int=0, shard_total: int=1,
                 event_loop: asyncio.AbstractEventLoop=None,
                 ):

        self.token = token
        self.socket_url = socket_url
        self.presence = presence
        self.shard_num = shard_num
        self.shard_total = shard_total

        if event_loop is None:  # Checking if event loop was passed in arguments
            self.event_loop = asyncio.get_event_loop()
            # If no loop was passed to the constructor default loop will be used
        else:
            self.event_loop = event_loop

        self.websocket = None  # The value will be assigned later during init_socket coroutine
        self.hello_payload = None  # The value will be assigned later during init_socket coroutine
        self.heartbeat_interval = None  # The value will be assigned later during init_socket coroutine
        self.heartbeat_sequence = None  # The value will be assigned later during init_socket coroutine

        self.ready_payload = None  # Assigned at _ready_event_trap
        self.session_id = None   # Assigned at _ready_event_trap

        self.event_hooks = []  # Event hooks that other functions can use to be notified of events
        #  Event hooks will be called with the dictionary payload each time a payload is received
        #  If the hook returns True boolean the hook will be removed

    async def _connect(self):
        self.websocket = await websockets.connect(self.socket_url, loop=self.event_loop)
        self.hello_payload = json.loads(await self.websocket.recv())
        self.heartbeat_interval = self.hello_payload['d']['heartbeat_interval'] / 1000

    async def _identify(self):
        payload = identity_template.copy()
        payload['token'] = self.token
        payload['presence'] = self.presence
        payload['shard'] = [self.shard_num, self.shard_total]

        async def ready_event_trap(event_payload: dict):
            if event_payload['t'] == 'READY':
                self.ready_payload = event_payload
                self.session_id = event_payload['d']['session_id']
                return True

        self.event_hook_add(ready_event_trap)
        await self.websocket.send(json.dumps({'op': 2, 'd': payload}))

    async def _heartbeat_cycle(self):
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await self.websocket.send(json.dumps({'op': 1, 'd': self.heartbeat_sequence}))

    async def _receive_cycle(self):
        while True:
            payload = await self.websocket.recv()
            if isinstance(payload, bytes):
                payload = str(zlib.decompress(payload), encoding='UTF-8')
            payload = json.loads(payload)
            if 's' in payload:
                self.heartbeat_sequence = payload['s']
            if payload['op'] == 11:  # discarding the op11 heartbeat ACK
                continue

            self.event_hooks[:] = [x for x in self.event_hooks if not await x(payload)]
            # NOTE: Right now event hooks block the receive queue. Maybe add a new function 'event_dispatcher'
            # that will be called with create_task and will be passed the payload to distribute to events
            # However, that might make events sequence be violated.

    async def init(self):
        await self._connect()
        await self._identify()
        self.event_loop.create_task(self._receive_cycle())
        self.event_loop.create_task(self._heartbeat_cycle())

    def event_hook_add(self, coroutine):
        self.event_hooks.append(coroutine)

    async def request_guild_members(self, guild_id: int, query: str = '', limit: int = 0):
        # TODO: implement query and limit support
        # BUG: Only returns 1000 users if there is more then 1000 users in the guild
        event = asyncio.Event()
        event.result = None

        async def func(x):
            # TODO: check that guild is the one requested
            if x['t'] == 'GUILD_MEMBERS_CHUNK':
                if x['d']['guild_id'] == str(guild_id):
                    event.result = x
                    event.set()

        self.event_hooks.append(func)
        await self.websocket.send(json.dumps({'op': 8, 'd': {
            "guild_id": guild_id,
            "query": query,
            "limit": limit
        }}))
        await event.wait()
        return event.result

    async def status_update(self, status_type: str, is_afk: bool,
                            game: dict = None, since_time_seconds: int = None)->asyncio.Task:
        if since_time_seconds is not None:
            since_time_seconds = str(since_time_seconds * 1000)
        return self.event_loop.create_task(self.websocket.send(json.dumps({
            'op': 3,
            'd': {
                'since': since_time_seconds,
                'game': game,
                'status': status_type,
                'afk': is_afk
            }
        }
        )))

    async def voice_state_update(self, guild_id: int, channel_id: int = None,
                                 mute_self: bool = None, deaf_self: bool = False):
        return self.event_loop.create_task(self.websocket.send(json.dumps({
            'op': 4,
            'd': {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'self_mute': mute_self,
                'self_deaf': deaf_self
            }

        }
        )))

    async def voice_server_ping(self):
        return self.event_loop.create_task(self.websocket.send(json.dumps({
            'op': 5,
            'd': None
        }
        )))

    async def resume(self):
        return self.event_loop.create_task(self.websocket.send(json.dumps({
            'op': 6,
            'd': {
                'token': self.token,
                'session_id': self.session_id,
                'seq': self.heartbeat_sequence
            }

        }
        )))
