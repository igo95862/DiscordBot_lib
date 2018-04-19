import typing

from .user import User
from ..client import DiscordClientAsync


class Reaction:

    def __init__(self, client_bind: DiscordClientAsync, count: int, me: bool, emoji: dict,
                 parent_message_id: str, parent_channel_id: str):
        self.client_bind = client_bind
        self.count = count
        self.me_reacted = me
        self.partial_emoji_dict = emoji
        self.parent_message_id = parent_message_id
        self.parent_channel_id = parent_channel_id

    async def user_reacted_async_gen(self) -> typing.AsyncGenerator[User, None]:
        async for x in self.client_bind.channel_message_reaction_iter_users(
                self.parent_message_id,
                self.parent_channel_id,
                self.partial_emoji_dict['id'] or self.partial_emoji_dict['name']):
            yield User(self.client_bind, **x)
