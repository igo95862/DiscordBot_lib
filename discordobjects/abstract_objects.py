from abc import ABC, abstractmethod
from .client import DiscordClientAsync
from typing import AsyncGenerator, Tuple, Type, Union, Sequence, List, Awaitable, Collection


class AbstractBase(ABC):

    @property
    @abstractmethod
    def snowflake(self) -> str:
        ...

    @property
    @abstractmethod
    def client_bind(self) -> DiscordClientAsync:
        ...

    def __eq__(self, other: 'AbstractBase'):
        return self.snowflake == other.snowflake

    def __hash__(self):
        return hash(self.snowflake)


class AbstractUser(AbstractBase):

    @property
    @abstractmethod
    def username(self) -> str:
        ...

    @property
    @abstractmethod
    def discriminator(self) -> str:
        ...

    @property
    @abstractmethod
    def avatar_hash(self) -> str:
        ...

    def get_avatar_url(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.snowflake}/{self.avatar_hash}.png"

    def get_name_formatted(self):
        return f"{self.username}#{self.discriminator}"

    def __str__(self):
        return f"<@{self.snowflake}>"

    def __repr__(self):
        return f"User: {self.get_name_formatted()} Id: {self.snowflake}"


class AbstractChannel(AbstractBase):

    @property
    @abstractmethod
    def type_int(self) -> int:
        pass


class MixinTextChannel(AbstractChannel):

    @property
    @abstractmethod
    def message_class(self) -> Type['AbstractMessage']:
        ...

    @abstractmethod
    async def message_iter_async_gen(self) -> AsyncGenerator['AbstractMessage', None]:
        ...

    @abstractmethod
    async def post_single_message_async(self, content: str, files: Tuple[str, bytes]) -> 'AbstractMessage':
        ...

    async def post_multi_message_async(
            self, content: Union[str, Sequence[str]], files: Sequence[Tuple[str, bytes]],) -> List['AbstractMessage']:
        pass


class AbstractMixinVoiceChannel(AbstractChannel):
    pass


class AbstractMessage(AbstractBase):

    @property
    @abstractmethod
    def content(self) -> str:
        ...

    @property
    @abstractmethod
    def parent_channel_id(self) -> str:
        ...

    def delete_async(self) -> Awaitable[bool]:
        return self.client_bind.channel_message_delete(self.parent_channel_id, self.snowflake)

    @abstractmethod
    def edit_async(self, new_content: str) -> 'AbstractMessage':
        ...


class AbstractGuild(AbstractBase):

    @property
    @abstractmethod
    def roles(self) -> Collection['AbstractGuildRole']:
        ...

    @property
    @abstractmethod
    def members(self) -> Collection['AbstractGuildMember']:
        ...

    @property
    @abstractmethod
    def channels(self) -> Collection['AbstractGuildMember']:
        ...


class AbstractGuildRole(AbstractBase):
    pass


class AbstractGuildMember(AbstractUser):
    pass


class AbstractGuildChannel(AbstractChannel):
    ...


class AbstractGuildChannelCategory(AbstractGuildChannel):
    pass


class AbstractGuildChannelText(AbstractGuildChannel, MixinTextChannel):
    pass

