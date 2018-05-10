from .base_object import DiscordObject
from ..client import DiscordClientAsync


class User(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, username: str, discriminator: str, avatar: str,
                 bot: bool = None, mfa_enabled: bool = None, verified: bool = None, email: str = None,
                 flags: int = None):
        super().__init__(client_bind, id)
        self.username = username
        self.discriminator = discriminator
        self.avatar_hash = avatar
        self.is_bot = bot
        self.mfa_enabled = mfa_enabled
        self.verified = verified
        self.email = email
        self.flags = flags

    def dm_open(self):
        pass

    def get_avatar_url(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.snowflake}/{self.avatar_hash}.png"

    def get_name_formatted(self) -> str:
        return f"{self.username}#{self.discriminator}"

    def __str__(self) -> str:
        return f"<@{self.snowflake}>"

    def __repr__(self) -> str:
        return f"User: {self.username}#{self.discriminator}"
