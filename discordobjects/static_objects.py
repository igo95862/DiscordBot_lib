from typing import Tuple, AsyncGenerator, Type, Collection, Dict, Set, FrozenSet, List, Optional
import logging
from .client import DiscordClientAsync
from .abstract_objects import (AbstractBase, AbstractUser, AbstractMixinTextChannel, AbstractMessage,
                               AbstractDmChannel, AbstractEmoji)


extra_keys_dict: Dict[str, Set[FrozenSet[str]]] = {}


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

    @classmethod
    def kwargs_handler(cls, **kwargs):
        if not kwargs:
            return

        extra_keys = frozenset(kwargs.keys())

        try:
            post_warning = extra_keys not in extra_keys_dict[cls.__name__]
        except KeyError:
            extra_keys_dict[cls.__name__] = set()
            post_warning = True

        if post_warning:
            extra_keys_dict[cls.__name__].add(extra_keys)
            logging.warning(
                (f"DiscordObject Initialization warning. Object {cls.__name__}"
                 f" was attempted to initialize with the keys: "
                 f"{', '.join((str(k) for k in kwargs.keys()))}"))


class StaticUser(StaticBase, AbstractUser):

    # noinspection PyShadowingBuiltins
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

    async def dm_open_async(self) -> 'StaticMessage':
        pass


class StaticMixinTextChannel(StaticBase, AbstractMixinTextChannel):

    @property
    def message_class(self) -> Type['AbstractMessage']:
        return StaticMessage

    async def get_last_message(self) -> 'StaticMessage':
        pass

    async def message_iter_async_gen(self) -> AsyncGenerator['StaticMessage', None]:
        async for x in self.client_bind.channel_message_iter(self.snowflake):
            yield StaticMessage(self.client_bind, **x)

    async def post_single_message_async(self, content: str, files: Tuple[str, bytes] = None) -> 'StaticMessage':
        new_message_dict = await self.client_bind.channel_message_create(self.snowflake, content, files_tuples=files)
        return StaticMessage(self.client_bind, **new_message_dict)


class StaticMessage(StaticBase, AbstractMessage):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, channel_id: str, author: dict, content: str,
                 timestamp: str, edited_timestamp: str, tts: bool, mention_everyone: bool, mentions: List[dict],
                 type: int, mention_roles: List[dict], attachments: List[dict], embeds: List[dict],
                 pinned: bool, reactions: List[dict] = None, nonce: bool = None, webhook_id: str = None,
                 guild_id: str = None, member: dict = None,
                 **kwargs):
        super().__init__(client_bind, id)
        self._parent_channel_id = channel_id
        self._author_dict = author
        self._content = content
        self._timestamp = timestamp
        self._edited_timestamp = edited_timestamp
        self._tts = tts
        self._mention_everyone = mention_everyone
        self._mentions_dicts = {x['id']: x for x in mentions}
        self._type = type
        self._mention_roles_dicts = mention_roles
        self._attachments_dicts = attachments
        self._embeds = embeds
        self._pinned = pinned
        self._reactions = reactions
        self._nonce = nonce
        self._webhook_id = webhook_id
        self._guild_id = guild_id
        self._member_dict = member

        self.kwargs_handler(**kwargs)

    @property
    def content(self) -> str:
        return self._content

    @property
    def author_user(self) -> AbstractUser:
        return StaticUser(self.client_bind, **self._author_dict)

    @property
    def author_member(self) -> AbstractUser:
        pass

    @property
    def parent_channel_id(self) -> str:
        return self._parent_channel_id

    def edit_async(self, new_content: str) -> 'AbstractMessage':
        pass

    @property
    def mentioned_users(self) -> Collection['AbstractUser']:
        pass

    @property
    def mentioned_members(self) -> Collection['AbstractGuildMember']:
        pass


class StaticDmChannel(StaticMixinTextChannel, AbstractDmChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, type: int, last_message_id: str,
                 recipients: List[dict], last_pin_timestamp: str = None,
                 **kwargs):
        super().__init__(client_bind, id)
        self._recipients_dicts = recipients
        self._type = type
        self._last_message_id = last_message_id
        self._last_pin_timestamp = last_pin_timestamp

        self.kwargs_handler(**kwargs)

    @property
    def type_int(self) -> int:
        return self._type

    @staticmethod
    async def load_async(client: DiscordClientAsync, user_id: str) -> 'StaticDmChannel':
        dm_dict = await client.dm_create(user_id)
        return StaticDmChannel(client, **dm_dict)


class StaticEmoji(AbstractEmoji):
    def __init__(self, name: str, id: str, roles: List[str] = None, user: Dict = None, require_colons: bool = None,
                 managed: bool = None, animated: bool = None, **kwargs):
        self._name = name
        self._emoji_id = id
        self._roles_ids = roles
        self._user_dict = user
        self._require_colons = require_colons
        self._managed = managed
        self._animated = animated

        # TODO: kwargs handler

    @property
    def name(self) -> str:
        return self._name

    @property
    def emoji_id(self) -> Optional[str]:
        return self._emoji_id

    @property
    def is_animated(self) -> bool:
        return self._animated


