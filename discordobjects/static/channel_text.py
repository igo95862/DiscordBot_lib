import typing

from .channel import Channel
from .message import Message
from ..discordclient import DiscordClient


class TextChannel(Channel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int, last_message_id: str,
                 last_pin_timestamp: str = None):
        super().__init__(client_bind, id, type)
        self.last_message_id = last_message_id
        self.last_pin_timestamp = last_pin_timestamp

    def post_message(self, content: str, force: bool = False) -> Message:
        if not force:
            if len(content) > 2000:
                raise TypeError('Message length can\'t be more then 2000 symbols')

        new_message_dict = self.client_bind.channel_message_create(self.snowflake, content)
        return Message(self.client_bind, **new_message_dict)

    def post_multi_message(self, content: str, break_char: str = '\n', threshold: int = 1000):
        max_length = 2000
        if len(content) <= max_length:
            self.post_message(content)
        else:
            curr_pos = 0
            while len(content) - curr_pos > max_length:
                next_break = content.rfind(break_char, curr_pos, curr_pos + max_length)
                if next_break != -1 and (curr_pos + next_break) > threshold:
                    self.post_message(content[curr_pos:next_break])
                    curr_pos = next_break
                else:
                    self.post_message(content[curr_pos:curr_pos + max_length])
                    curr_pos += max_length
            self.post_message(content[curr_pos:])

    def post_file(self, file_name: str, file_bytes: bytes):
        return Message(self.client_bind, **self.client_bind.channel_message_create_file(self.snowflake,
                                                                                        file_name, file_bytes))

    def message_iter(self) -> typing.Generator[Message, None, None]:
        yield from (Message(self.client_bind, **x) for x in self.message_dict_iter())

    def message_dict_iter(self) -> typing.Generator[dict, None, None]:
        yield from self.client_bind.channel_message_iter(self.snowflake)

    def get_last_message(self) -> Message:
        return Message(self.client_bind, **self.client_bind.channel_message_get(self.snowflake, self.last_message_id))

    async def on_message_created(self) -> typing.AsyncGenerator[Message, None]:
        async for message_dict in self.client_bind.event_gen_message_create():
            if message_dict['channel_id'] == self.snowflake:
                yield Message(self.client_bind, **message_dict)
