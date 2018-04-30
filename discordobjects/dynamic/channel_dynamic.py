import asyncio
import typing


from collections import deque
from ..static import Message, GuildTextChannel
from .base_dynamic import BaseDynamic
from ..client import DiscordClientAsync


class GuildTextChannelDynamic(BaseDynamic):

    def __init__(self, client_bind: DiscordClientAsync, channel_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True):
        self.channel_id = channel_id
        self.message_deque: typing.Deque[Message] = deque()

        super().__init__(client_bind, ('MESSAGE_CREATE', 'MESSAGE_UPDATE', 'MESSAGE_DELETE'),
                         event_loop, start_immediately)