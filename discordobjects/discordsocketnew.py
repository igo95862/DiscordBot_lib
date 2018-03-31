import asyncio
import json
import logging
import typing
import zlib
from functools import partial

import websockets

identity_template = {
    'properties':
        {
            "$os": 'Python',
            "$device": 'Python',
            "$browser": "Discord Objects (dob)"
        },
    'compress': True,
    "large_threshold": 250,
}


class DiscordSocket:

    def __init__(self, token,
                 socket_url='wss://gateway.discord.gg/?v=6&encoding=json',
                 presence={'status': 'online', 'afk': False}.copy(),
                 shard_num: int = 0, shard_total: int = 1,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 event_handler: typing.Callable[[dict], None] = print
                 ):

        self.token = token
        self.socket_url = socket_url
        self.presence = presence
        self.shard_num = shard_num
        self.shard_total = shard_total

        self.event_loop = event_loop
        self.running: bool = True

        self.hello_payload: dict = None
        self.heartbeat_interval: float = None
        self.heartbeat_sequence: int = None

        self.ready_payload: dict = None
        self.session_id = None

        self.event_handler = event_handler

    async def init(self) -> None:
        heart_beat = None
        while self.running:
            try:
                async with websockets.connect(self.socket_url, timeout=1, loop=self.event_loop) as discord_socket:
                    self.hello_payload = json.loads(await discord_socket.recv())
                    self.heartbeat_interval = self.hello_payload['d']['heartbeat_interval'] / 1000

                    if self.session_id is None:
                        await self._identify(discord_socket)
                    else:
                        await self._reconnect(discord_socket)

                    heart_beat = self.event_loop.create_task(self._heartbeat_cycle(discord_socket))

                    async for message in discord_socket:
                        if isinstance(message, bytes):
                            message = str(zlib.decompress(message), encoding='UTF-8')
                        payload = json.loads(message)
                        if 's' in payload:
                            self.heartbeat_sequence = payload['s']
                        if payload['op'] == 11:  # discarding the op11 heartbeat ACK
                            continue
                        elif payload['op'] == 9:
                            await asyncio.sleep(4)
                            await self._identify(discord_socket)
                            continue
                        elif payload['t'] == 'READY':
                            self.ready_payload = payload
                            self.session_id = payload['d']['session_id']

                        self.event_loop.call_soon(partial(self.event_handler, payload))
            except websockets.exceptions.ConnectionClosed:
                if isinstance(heart_beat, asyncio.Task):
                    if not heart_beat.cancelled():
                        heart_beat.cancel()
            except Exception as e:
                logging.exception(e)
                raise
            else:
                self.running = False
                if isinstance(heart_beat, asyncio.Task):
                    if not heart_beat.cancelled():
                        heart_beat.cancel()

    async def _heartbeat_cycle(self, websocket) -> None:
        while self.running:
            await asyncio.sleep(self.heartbeat_interval)
            await websocket.send(json.dumps({'op': 1, 'd': self.heartbeat_sequence}))

    async def _reconnect(self, websocket) -> None:
        await websocket.send(json.dumps(
            {'op': 6, 'd': {'token': self.token, 'session_id': self.session_id, 'seq': self.heartbeat_sequence}}))

    async def _identify(self, websocket) -> None:
        identify_payload = identity_template.copy()
        identify_payload['token'] = self.token
        identify_payload['presence'] = self.presence
        identify_payload['shard'] = [self.shard_num, self.shard_total]
        await websocket.send(json.dumps({'op': 2, 'd': identify_payload}))

    async def set_event_handler(self, new_event_handler: typing.Callable[[dict], None]):
        self.event_handler = new_event_handler
