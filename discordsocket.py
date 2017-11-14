import websockets
import asyncio
import queue
import threading
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




class DiscordWebsocket:
    def __init__(self, token,
                 socket_url='wss://gateway.discord.gg/?v=6&encoding=json',
                 presence={'status': 'online', 'afk': False}.copy(),
                 shard_num=0, shard_total=1,
                 receive_queue=None, block_receive_queue=False,
                 event_loop: asyncio.AbstractEventLoop=None,
                 discard_events=False):

        self.token = token
        self.socket_url = socket_url
        self.presence = presence
        self.shard_num = shard_num
        self.shard_total = shard_total
        self.block_receive_queue = block_receive_queue
        self.discard_events = discard_events

        if receive_queue is None:  # Checking if the queue was passed in arguments
            self.receive_queue = queue.Queue()  # Creating a new one if no queue was passed
        else:
            self.receive_queue = receive_queue

        if event_loop is None:  # Checking if event loop was passed in arguments
            self.event_loop = asyncio.get_event_loop()
            # If no loop was passed to the constructor default loop will be used
        else:
            self.event_loop = event_loop

        self.websocket = None  # The value will be assigned later during init_socket coroutine
        self.helloPayload = None  # The value will be assigned later during init_socket coroutine
        self.heartbeatInterval = None  # The value will be assigned later during init_socket coroutine
        self.heartbeat_sequence = None  # The value will be assigned later during init_socket coroutine

        self.event_hooks = []  # Event hooks that other functions can use to be notified of events

    async def _connect(self):
        if self.event_loop is not None:
            self.websocket = await websockets.connect(self.socket_url, loop=self.event_loop)
            self.helloPayload = json.loads(await self.websocket.recv())
            self.heartbeatInterval = self.helloPayload['d']['heartbeat_interval'] / 1000
        else:
            raise Exception('No event loop defined.')

    async def _identify(self):
        payload = identity_template.copy()
        payload['token'] = self.token
        payload['presence'] = self.presence
        payload['shard'] = [self.shard_num, self.shard_total]
        await self.websocket.send(json.dumps({'op': 2, 'd': payload}))

    async def _heartbeat_cycle(self):
        while True:
            await asyncio.sleep(self.heartbeatInterval)
            await self.websocket.send(json.dumps({'op': 1, 'd': self.heartbeat_sequence }))

    async def _receive_cycle(self):
        while True:
            payload = await self.websocket.recv()
            if isinstance(payload, bytes):
                payload = str(zlib.decompress(payload), encoding='UTF-8')
            payload = json.loads(payload)
            if 's' in payload:
                self.heartbeat_sequence = payload['s']
            if payload['op'] == 11 or self.discard_events:  # discarding the op11 heartbeat ACK
                # or of discard events is true
                continue

            for f in self.event_hooks:
                await f(payload)

            try:
                self.receive_queue.put(payload, block=self.block_receive_queue)
            except queue.Full:
                continue

    async def init(self):
        await self._connect()
        await self._identify()
        self.event_loop.create_task(self._receive_cycle())
        self.event_loop.create_task(self._heartbeat_cycle())

    async def request_guild_members(self, guild_id: int, query: str = '', limit: int = 0):
        event = asyncio.Event()
        event.result = None
        async def func(x):
            if x['t'] == 'GUILD_MEMBERS_CHUNK':
                event.set()
                event.result = x

        self.event_hooks.append(func)
        await self.websocket.send(json.dumps({'op': 8, 'd': {
            "guild_id": guild_id,
            "query": query,
            "limit": limit
        }}))
        await event.wait()
        return event.result



class DiscordWebsocketThread:

    def __init__(self, discord_websocket: DiscordWebsocket):
        self.discord_websocket = discord_websocket
        self.discord_websocket_loop = asyncio.new_event_loop()
        self.discord_websocket.event_loop = self.discord_websocket_loop

        self.thread = threading.Thread(target=self.discord_websocket_loop.run_forever)
        self.thread.start()

        connect_future = asyncio.run_coroutine_threadsafe(self.discord_websocket._connect(),
                                                          self.discord_websocket_loop)
        connect_future.result(timeout=5)

        identify_future = asyncio.run_coroutine_threadsafe(self.discord_websocket._identify(),
                                                           self.discord_websocket_loop)
        identify_future.result(timeout=5)

        self.hearbeat_future =  asyncio.run_coroutine_threadsafe(self.discord_websocket._heartbeat_cycle(),
                                                                 self.discord_websocket_loop)
        self.receive_future = asyncio.run_coroutine_threadsafe(self.discord_websocket._receive_cycle(),
                                                               self.discord_websocket_loop)

    def request_guild_members(self, guild_id: int, query: str = '', limit: int = 0):
        return asyncio.run_coroutine_threadsafe(self.discord_websocket.request_guild_members(guild_id, query, limit),
                                                self.discord_websocket_loop)






























'''
class DiscordWebsocketsContainer():

    def __init__(self, wssURL = 'wss://gateway.discord.gg/?v=6&encoding=json'):

        self.internalLoop = asyncio.new_event_loop()
        self.receiveQueue = queue.Queue()
        self.sendQueue = queue.Queue()

        self.internalLoop.create_task(self.init_socket())
        self.internalThread = threading.Thread(target=self.internalLoop.run_forever)
        self.internalThread.start()

    async def init_socket(self):
        self.websocket = await websockets._connect('wss://gateway.discord.gg/?v=6&encoding=json')

        self.helloPayload = json.loads(await self.websocket.recv())

        self.heartbeatInterval = self.helloPayload['d']['heartbeat_interval'] / 1000

        await self.indetify()

        self.d = None

        self.taskRecieve = asyncio.ensure_future(self.recieveWaiter())

        self.taskHeartbeat = asyncio.ensure_future(self.heartbeat())



    async def indetify(self):
        payload = {}
        payload['op'] = 2
        payload['d'] = i
        await self.websocket.send(json.dumps(payload))

    async def heartbeat(self):
        while True:
            await asyncio.sleep(self.heartbeatInterval)
            await self.websocket.send(json.dumps({'op': 1, 'd': self.d }))

    async def recieveWaiter(self):
        while True:
            payload = await self.websocket.recv()
            if isinstance(payload, bytes):
                payload = zlib.decompress(payload)
            payload = json.loads(payload)


            if payload['op'] == 11: #discarding the op11 heartbeat ACK
                continue

            self.receiveQueue.put(payload)

    def getAllRecieveQueue(self):
        list = []
        while (not self.receiveQueue.empty()):
            list.append(self.receiveQueue.get(timeout=5))
        return list


a = DiscordWebsocket()
'''