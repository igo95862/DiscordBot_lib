from abc import ABC, abstractmethod
from .client import DiscordClientAsync
from typing import AsyncGenerator, Tuple, Type, Union, Sequence, List, Optional, Collection, Iterable, Mapping
from .constants import MESSAGE_MAX_LENGTH
from .util import EventDispenser


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

    @abstractmethod
    async def dm_open_async(self) -> 'AbstractDmChannel':
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
        ...

    async def delete_async(self):
        await self.client_bind.channel_delete(self.snowflake)


def split_message(total_text: str, break_chars: Sequence[str] = ('\n', '.', ','), threshold: int = 1000) -> List[str]:
    if isinstance(total_text, str):
        # Preform split
        max_length = MESSAGE_MAX_LENGTH
        message_fragments = []
        curr_pos = 0
        while len(total_text) - curr_pos > max_length:
            for bc in break_chars:
                next_break = total_text.rfind(bc, curr_pos, curr_pos + max_length)
                if next_break != -1 and (curr_pos + next_break) > threshold:
                    message_fragments.append(total_text[curr_pos:next_break])
                    curr_pos = next_break
                    break

            else:
                message_fragments.append(total_text[curr_pos:curr_pos + max_length])
                curr_pos += max_length

        message_fragments.append(total_text[curr_pos:])
    else:
        message_fragments = total_text

    return message_fragments


class AbstractMixinTextChannel(AbstractChannel):

    @property
    @abstractmethod
    def message_class(self) -> Type['AbstractMessage']:
        ...

    @abstractmethod
    async def get_last_message(self) -> 'AbstractMessage':
        ...

    @abstractmethod
    async def message_iter_async_gen(self) -> AsyncGenerator['AbstractMessage', None]:
        ...

    @abstractmethod
    async def post_single_message_async(self, content: str, files: Tuple[str, bytes] = None) -> 'AbstractMessage':
        ...

    async def post_multi_message_async(
            self, content: Union[str, Iterable[str]], files: Sequence[Tuple[str, bytes]] = None ,
            break_chars: Sequence[str] = ('\n', '.', ','), threshold: int = 1000
    ) -> List['AbstractMessage']:

        return [await self.post_single_message_async(x) for x in split_message(content, break_chars, threshold)]

    @property
    @abstractmethod
    def event_message_created(self) -> EventDispenser['AbstractMessage']:
        ...


class AbstractMixinVoiceChannel(AbstractChannel):
    ...


class AbstractDmChannel(AbstractMixinTextChannel):
    ...


class AbstractGroupDmChannel(AbstractMixinTextChannel):
    ...


class AbstractMessage(AbstractBase):

    @property
    @abstractmethod
    def content(self) -> str:
        ...

    @property
    @abstractmethod
    def author_user(self) -> AbstractUser:
        ...

    @property
    @abstractmethod
    def author_member(self) -> 'AbstractGuildMember':
        ...

    @property
    @abstractmethod
    def parent_channel_id(self) -> str:
        ...

    async def delete_async(self):
        await self.client_bind.channel_message_delete(self.parent_channel_id, self.snowflake)

    @abstractmethod
    async def edit_async(self, new_content: str) -> 'AbstractMessage':
        ...

    async def add_reaction_async(self, emoji_name: Union[str, 'AbstractEmoji'], emoji_id: str = None):
        if isinstance(emoji_name, AbstractEmoji):
            emoji_id = emoji_name.emoji_id
            emoji_name = emoji_name.name

        if emoji_id is None:
            final_string = emoji_name
        else:
            final_string = f"{emoji_name}:{emoji_id}"

        await self.client_bind.channel_message_reaction_create(self.parent_channel_id, self.snowflake, final_string)

    async def clear_users_reaction_async(self, user: Union[str, AbstractUser],
                                         emoji_name: Union[str, 'AbstractEmoji'], emoji_id: str = None):

        if isinstance(user, AbstractUser):
            user_id = user.snowflake
        else:
            user_id = user

        if isinstance(emoji_name, AbstractEmoji):
            emoji_id = emoji_name.emoji_id
            emoji_name = emoji_name.name

        if emoji_id is None:
            final_string = emoji_name
        else:
            final_string = f"{emoji_name}:{emoji_id}"

        await self.client_bind.channel_message_reaction_delete(
            self.parent_channel_id, self.snowflake, user_id, final_string)

    async def clear_all_reaction_async(self):
        await self.client_bind.channel_message_reaction_delete_all(self.parent_channel_id, self.snowflake)

    @property
    @abstractmethod
    def event_message_reaction_add(self) -> EventDispenser:
        ...

    @property
    @abstractmethod
    def event_message_reaction_remove(self) -> EventDispenser:
        ...

    @property
    @abstractmethod
    def mentioned_users(self) -> Collection['AbstractUser']:
        ...

    @property
    @abstractmethod
    def mentioned_members(self) -> Collection['AbstractGuildMember']:
        ...

    @abstractmethod
    async def reply_async(self, content: str) -> 'AbstractMessage':
        ...

    async def reply_multiple_async(self, content: str) -> List['AbstractMessage']:
        return [await self.reply_async(x) for x in split_message(content)]


class AbstractEmoji(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def emoji_id(self) -> Optional[str]:
        ...

    @property
    @abstractmethod
    def is_animated(self) -> bool:
        ...

    @property
    def is_unicode(self) -> bool:
        return self.emoji_id is None

    def __str__(self):
        if self.is_unicode:
            return self.name
        else:
            return f"<:{self.name}:{self.emoji_id}>"

    def __eq__(self, other: Union[str, 'AbstractEmoji']):
        if isinstance(other, str) and self.is_unicode:
            return self.name == other
        elif isinstance(other, AbstractEmoji):
            return self.emoji_id == other.emoji_id
        else:
            raise TypeError(f"Cannot make comparison between AbtractEmoji and {other.__class__}")

    def __hash__(self):
        if self.is_unicode:
            return hash(self.name)
        else:
            return hash(self.name + self.emoji_id)


class AbstractAttachment(ABC):

    @property
    @abstractmethod
    def height(self) -> Optional[int]:
        ...

    @property
    @abstractmethod
    def width(self) -> Optional[int]:
        ...

    def is_image(self) -> bool:
        return self.height is not None


class AbstractGuild(AbstractBase):

    @property
    @abstractmethod
    def emojis(self) -> Mapping[str, 'AbstractEmoji']:
        ...

    @property
    @abstractmethod
    def roles(self) -> Mapping[str, 'AbstractGuildRole']:
        ...

    @property
    @abstractmethod
    def members(self) -> Mapping[str, 'AbstractGuildMember']:
        ...

    @property
    @abstractmethod
    def text_channels(self) -> Mapping[str, 'AbstractGuildChannelText']:
        ...

    @property
    @abstractmethod
    def voice_channels(self) -> Mapping[str, 'AbstractGuildChannelVoice']:
        ...

    @property
    @abstractmethod
    def category_channels(self) -> Mapping[str, 'AbstractGuildChannelCategory']:
        ...


class AbstractGuildRole(AbstractBase):
    @property
    @abstractmethod
    def role_name(self) -> str:
        ...

    @property
    @abstractmethod
    def role_color(self) -> int:
        ...

    @property
    @abstractmethod
    def display_separately(self) -> bool:
        ...

    @property
    @abstractmethod
    def position(self) -> int:
        ...

    @property
    @abstractmethod
    def permissions_int(self) -> int:
        ...

    @property
    @abstractmethod
    def is_managed(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_mentionable(self) -> bool:
        ...

    @property
    @abstractmethod
    def parent_guild_id(self) -> str:
        ...

    def __repr__(self) -> str:
        return f"Role: {self.role_name} Id: {self.snowflake}"


class AbstractGuildMember(AbstractUser):

    @property
    @abstractmethod
    def role_ids(self) -> List[str]:
        ...

    def __contains__(self, item: Union[AbstractGuildRole, str]):
        if isinstance(item, AbstractGuildRole):
            return item.snowflake in self.role_ids
        elif isinstance(item, str):
            return item in self.role_ids
        else:
            raise TypeError(f" in Guild Member accepts Abstract Role or str, got {item.__class__}")


class AbstractGuildChannel(AbstractChannel):
    @property
    @abstractmethod
    def guild_id(self) -> str:
        ...

    async def edit_permission_async(
            self, subject: Union[AbstractUser, AbstractGuildRole], allow_permissions: int, deny_permissions: int):

        if isinstance(subject, AbstractUser):
            subject_type = 'member'
        elif isinstance(subject, AbstractGuildRole):
            subject_type = 'role'
        else:
            raise TypeError(f"edit_permission called with wrong type. Got {subject.__class__},"
                            f" expected {Union[AbstractUser, AbstractGuildRole]}")

        await self.client_bind.channel_permissions_overwrite_edit(self.snowflake, subject.snowflake,
                                                                  allow_permissions, deny_permissions, subject_type)


class AbstractGuildChannelCategory(AbstractGuildChannel):
    pass


class AbstractGuildChannelText(AbstractGuildChannel, AbstractMixinTextChannel):
    pass


class AbstractGuildChannelVoice(AbstractGuildChannel, AbstractMixinVoiceChannel):

    async def move_member_to_async(self, member: AbstractGuildMember):
        await self.client_bind.guild_member_modify(self.guild_id, member.snowflake,new_channel_id=self.snowflake)

