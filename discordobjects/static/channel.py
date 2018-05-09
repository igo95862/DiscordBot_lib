from .base_object import DiscordObject
from ..client import DiscordClientAsync


class Channel(DiscordObject):
    CHANNEL_TYPE_GUILD_TEXT = 0
    CHANNEL_TYPE_DM = 1
    CHANNEL_TYPE_GUILD_VOICE = 2
    CHANNEL_TYPE_GROUP_DM = 3
    CHANNEL_TYPE_GUILD_CATEGORY = 4

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, type: int):
        super().__init__(client_bind, id)
        self.channel_type = type

    async def modify_name_async(self, new_name: str) -> 'Channel':
        return self.__class__(
            self.client_bind, **(await self.client_bind.channel_modify(self.snowflake, new_name=new_name)))

    async def modify_position_async(self, new_position: int) -> 'Channel':
        return self.__class__(
            self.client_bind, **(await self.client_bind.channel_modify(self.snowflake, new_position=new_position)))
