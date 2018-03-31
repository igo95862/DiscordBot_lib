import typing

from .user import User
from ..discordclient import DiscordClient


class Reaction:

    def __init__(self, client_bind: DiscordClient, count: int, me: bool, emoji: dict,
                 parent_message_id: str, parent_channel_id: str):
        self.client_bind = client_bind
        self.count = count
        self.me_reacted = me
        self.partial_emoji_dict = emoji
        self.parent_message_id = parent_message_id
        self.parent_channel_id = parent_channel_id

    def user_reacted_gen(self) -> typing.Generator[User, None, None]:
        yield from (User(self.client_bind, **x) for x in self.client_bind.channel_message_reaction_iter_users(
            self.parent_message_id,
            self.parent_channel_id,
            self.partial_emoji_dict['id'] or self.partial_emoji_dict['name']))
