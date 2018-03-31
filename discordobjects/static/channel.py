from .base_object import DiscordObject
from ..discordclient import DiscordClient


class Channel(DiscordObject):
    CHANNEL_TYPE_GUILD_TEXT = 0
    CHANNEL_TYPE_DM = 1
    CHANNEL_TYPE_GUILD_VOICE = 2
    CHANNEL_TYPE_GROUP_DM = 3
    CHANNEL_TYPE_GUILD_CATEGORY = 4

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int):
        super().__init__(client_bind, id)
        self.channel_type = type
