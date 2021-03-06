import typing

from .attachment import Attachment
from .base_object import DiscordObject
from .emoji import Emoji
from .reaction import Reaction
from .user import User
from ..client import DiscordClientAsync
from ..util import SingularEvent


class Message(DiscordObject):
    MESSAGE_TYPE_DEFAULT = 0
    MESSAGE_TYPE_RECIPIENT_ADD = 1
    MESSAGE_TYPE_RECIPIENT_REMOVE = 2
    MESSAGE_TYPE_CALL = 3
    MESSAGE_TYPE_CHANNEL_NAME_CHANGE = 4
    MESSAGE_TYPE_CHANNEL_ICON_CHANGE = 5
    MESSAGE_TYPE_CHANNEL_PINNED_MESSAGE = 6
    MESSAGE_TYPE_GUILD_MEMBER_JOIN = 7

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, channel_id: str, author: dict, content: str,
                 timestamp: str, edited_timestamp: str, tts: bool, mention_everyone: bool, mentions: typing.List[dict],
                 type: int, mention_roles: typing.List[dict], attachments: typing.List[dict], embeds: typing.List[dict],
                 pinned: bool, reactions: typing.List[dict] = None, nonce: bool = None, webhook_id: str = None,
                 guild_id: str = None, member: dict = None,
                 **kwargs):
        super().__init__(client_bind, id)
        self.parent_channel_id = channel_id
        self.author_dict = author
        self.content = content
        self.timestamp = timestamp
        self.edited_timestamp = edited_timestamp
        self.tts = tts
        self.mention_everyone = mention_everyone
        self.mentions_dicts = {x['id']: x for x in mentions}
        self.type = type
        self.mention_roles_dicts = mention_roles
        self.attachments_dicts = attachments
        self.embeds = embeds
        self.pinned = pinned
        self.reactions = reactions
        self.nonce = nonce
        self.webhook_id = webhook_id
        self.guild_id = guild_id
        self.member_dict = member

        self.kwargs_handler(**kwargs)

    def update_from_dict(self, message_dict: dict) -> None:
        self.__init__(self.client_bind, **message_dict)

    async def refresh_async(self) -> None:
        await self.update_from_dict(self.client_bind.channel_message_get(self.parent_channel_id, self.snowflake))

    async def edit_async(self, new_content: str) -> None:
        self.update_from_dict(
            await self.client_bind.channel_message_edit(self.parent_channel_id, self.snowflake, new_content))

    async def remove_async(self) -> None:
        await self.client_bind.channel_message_delete(self.parent_channel_id, self.snowflake)

    async def add_unicode_emoji_async(self, unicode_emoji: str):
        await self.client_bind.channel_message_reaction_create(self.parent_channel_id, self.snowflake, unicode_emoji)

    async def clear_emoji_by_user(self, emoji: Emoji, user: typing.Union[User, str]):
        if isinstance(user, User):
            user_id = user.snowflake
        else:
            user_id = user

        await self.client_bind.channel_message_reaction_delete(
            self.parent_channel_id, self.snowflake, user_id, emoji.util_id())

    async def clear_all_emoji_async(self) -> None:
        await self.client_bind.channel_message_reaction_delete_all(self.parent_channel_id, self.snowflake)

    async def reacted_users_by_unicode_emoji_async_gen(self, unicode_emoji: str) -> typing.AsyncGenerator['User', None]:
        async for d in self.client_bind.channel_message_reaction_iter_users(
                self.parent_channel_id, self.snowflake, unicode_emoji):
            yield User(self.client_bind, **d)

    async def get_reactions_async(self) -> typing.List[Reaction]:
        await self.refresh_async()
        if self.reactions is not None:
            return [Reaction(self.client_bind, **x,
                             parent_message_id=self.snowflake, parent_channel_id=self.parent_channel_id)
                    for x in self.reactions]
        else:
            return []

    def get_content(self) -> str:
        return self.content

    def get_author(self) -> User:
        return User(self.client_bind, **self.author_dict)

    def is_author(self, user: User) -> bool:
        return user.snowflake == self.author_dict['id']

    def get_mentioned_users(self) -> typing.List[User]:
        return [User(self.client_bind, **self.mentions_dicts[x]) for x in self.mentions_dicts]

    def get_mentioned_users_ids(self) -> typing.List[str]:
        return [self.mentions_dicts[x]['id'] for x in self.mentions_dicts]

    def attachments_iter(self) -> typing.Generator[Attachment, None, None]:
        for d in self.attachments_dicts:
            yield Attachment(self.client_bind, **d)

    def event_user_add_reaction_any_async(self, user: User) -> typing.Coroutine[typing.Any, typing.Any, Emoji]:
        def condition(event_dict: dict, event_name: str):
            if event_dict['channel_id'] == self.parent_channel_id:
                if event_dict['message_id'] == self.snowflake:
                    return event_dict['user_id'] == user.snowflake
            return False

        event = SingularEvent(condition)
        self.client_bind.socket_thread.event_queue_add_single(event, 'MESSAGE_REACTION_ADD')

        async def return_courutine():
            return Emoji(**((await event)[0]['emoji']))

        return return_courutine()

    async def on_emoji_created_async_gen(self) -> typing.AsyncGenerator[typing.Tuple[Emoji, str], None]:
        async for reaction_dict in self.client_bind.event_gen_message_reaction_add():
            if reaction_dict['channel_id'] == self.parent_channel_id:
                if reaction_dict['message_id'] == self.snowflake:
                    # TODO: hande custom versus unicode emojies correctly
                    yield Emoji(**reaction_dict['emoji']), reaction_dict['user_id']
