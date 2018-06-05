import asyncio
import logging
import typing
import weakref

from ..client import DiscordClientAsync
from ..constants import SocketEventNames, ChannelTypes
from ..static import GuildTextChannel, GuildVoiceChannel, GuildCategory
from .base_dynamic import BaseDynamic
from .voice_state import VoiceStateManager


class LiveGuildChannels(BaseDynamic):

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str,
                 voice_state_manager: VoiceStateManager = None,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True):
        self.guild_id = guild_id
        self.channels: typing.Dict[str, typing.Union[GuildTextChannel, GuildCategory, GuildVoiceChannel]] = None
        if voice_state_manager is not None:
            self.voice_state_manager = voice_state_manager
        else:
            self.voice_state_manager = VoiceStateManager(client_bind, event_loop, start_immediately)

        super().__init__(client_bind, ('ADD', 'UPDATE', 'REMOVE'), event_loop, start_immediately)

    async def _auto_update(self):
        await self.voice_state_manager
        self.channels = {x['id']: self._resolve_channel_class(x)(client_bind=self.client_bind, **x)
                         for x in await self.client_bind.guild_channel_list(self.guild_id)}

        self.await_init.set_result(True)

        async for event_dict, event_name in self.client_bind.event_gen_multiple(
                (SocketEventNames.CHANNEL_CREATE, SocketEventNames.CHANNEL_UPDATE, SocketEventNames.CHANNEL_DELETE)):
            try:
                guild_id = event_dict['guild_id']
            except KeyError:
                continue

            if guild_id != self.guild_id:
                continue

            if event_name == SocketEventNames.CHANNEL_CREATE:
                self._channel_create(event_dict)
            elif event_name == SocketEventNames.CHANNEL_UPDATE:
                self._channel_update(event_dict)
            elif event_name == SocketEventNames.CHANNEL_DELETE:
                self._channel_delete(event_dict)
            else:
                logging.error(f"LiveGuildChannels received unpredicted event of the name {event_name}")

    def _resolve_channel_class(self, channel_dict: dict) -> type:
        channel_type = channel_dict['type']
        if channel_type == ChannelTypes.GUILD_CATEGORY:
            return GuildCategory
        elif channel_type == ChannelTypes.GUILD_TEXT:
            return GuildTextChannel
        elif channel_type == ChannelTypes.GUILD_VOICE:
            channel_dict['voice_manager_bind'] = self.voice_state_manager
            return LinkedGuildVoiceChannel
        else:
            logging.error(f"LiveGuildChannels _channel_create mismatched channel type. Got: {channel_type}")

    def _channel_create(self, event_dict: dict):
        channel_id = event_dict['id']
        channel_class = self._resolve_channel_class(event_dict)
        self.channels[channel_id] = channel_class(self.client_bind, **event_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('ADD', weakref.proxy(self.channels[channel_id])))

    def _channel_update(self, event_dict: dict):
        channel_id = event_dict['id']
        try:
            old_channel = self.channels[channel_id]
        except KeyError:
            logging.warning(f"Attempted to update channel that does not have record. Id: {channel_id}")
            self._channel_create(event_dict)
            return

        old_channel.__init__(self.client_bind, **event_dict)
        asyncio.ensure_future(self.queue_dispenser.event_put('UPDATE', weakref.proxy(self.channels[channel_id])))

    def _channel_delete(self, event_dict: dict):
        channel_id = event_dict['id']

        old_channel = self.channels.pop(channel_id)

        asyncio.ensure_future(self.queue_dispenser.event_put('REMOVE', old_channel))

    def __getitem__(self, item):
        return weakref.proxy(self.channels[item])


class LinkedGuildVoiceChannel(GuildVoiceChannel):

    def __init__(self, voice_manager_bind: VoiceStateManager, **kwargs):
        self.voice_manager_bind = voice_manager_bind
        super().__init__(**kwargs)

    async def on_user_join(self):
        async for user_id, channel_id in self.voice_manager_bind.on_user_join_channel():
            if channel_id == self.snowflake:
                yield user_id

    async def on_user_leave(self):
        async for user_id, channel_id in self.voice_manager_bind.on_user_left_channel():
            if channel_id == self.snowflake:
                yield user_id

