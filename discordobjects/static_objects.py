from .client import DiscordClientAsync
from .abstract_objects import AbstractBase, AbstractUser


class StaticBase(AbstractBase):

    def __init__(self, client_bind: DiscordClientAsync, id: str):
        self._client_bind = client_bind
        self._snowflake = id

    @property
    def snowflake(self) -> str:
        return self._snowflake

    @property
    def client_bind(self) -> DiscordClientAsync:
        return self._client_bind


class StaticUser(StaticBase, AbstractUser):

    def __init__(
            self, client_bind: DiscordClientAsync, id: str, username: str, discriminator: str, avatar: str,
            bot: bool = None, mfa_enabled: bool = None, verified: bool = None, email: str = None,
            flags: int = None, ):
        super().__init__(client_bind, id)
        self._username = username
        self._discriminator = discriminator
        self._avatar_hash = avatar
        self._is_bot = bot
        self._mfa_enabled = mfa_enabled
        self._verified = verified
        self._email = email
        self._flags = flags

    @property
    def username(self) -> str:
        return self._username

    @property
    def discriminator(self) -> str:
        return self._discriminator

    @property
    def avatar_hash(self) -> str:
        return self._avatar_hash
