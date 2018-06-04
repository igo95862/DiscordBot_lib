import asyncio
import logging
import typing
import weakref

from ..client import DiscordClientAsync
from ..constants import SocketEventNames
from ..static import GuildTextChannel, GuildVoiceChannel, GuildCategory
from .base_dynamic import BaseDynamic


class LiveGuildRoles(BaseDynamic):

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True):
        self.guild_id = guild_id
        self.channels: typing.Dict[str, typing.Union[GuildTextChannel, GuildCategory, GuildVoiceChannel]] = None

        super().__init__(client_bind, ('ADD', 'UPDATE', 'REMOVE'), event_loop, start_immediately)

    async def _auto_update(self):
        self.channels = {x['id']: x async for x in self.client_bind.guild_channel_list(self.guild_id)}

        self.await_init.set_result(True)

        async for event_dict, event_name in self.client_bind.event_gen_multiple(
                (SocketEventNames.CHANNEL_CREATE, SocketEventNames.CHANNEL_UPDATE, SocketEventNames.CHANNEL_DELETE)):
            pass
