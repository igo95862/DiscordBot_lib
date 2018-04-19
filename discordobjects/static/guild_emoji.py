import typing

from .base_object import DiscordObject
from ..client import DiscordClientAsync


class CustomEmoji(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, name: str, roles: typing.List[int], user: dict,
                 require_colons: bool, managed: bool, animated: bool):
        super().__init__(client_bind, id)
        self.emoji_name = name
        self.roles_allowed = roles
        self.user_creator_dict = user
        self.require_colons = require_colons
        self.managed = managed
        self.animated = animated

    def get_url(self) -> str:
        return f"https://cdn.discordapp.com/emojis/{self.snowflake}.png"
