import typing

from .channel import Channel
from .message import Message
from ..client import DiscordClientAsync


class TextChannel(Channel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, type: int, last_message_id: str,
                 last_pin_timestamp: str = None):
        super().__init__(client_bind, id, type)
        self.last_message_id = last_message_id
        self.last_pin_timestamp = last_pin_timestamp

    async def post_message_async(self, content: str, force: bool = False) -> Message:
        if not force:
            if len(content) > 2000:
                raise TypeError('Message length can\'t be more then 2000 symbols')

        new_message_dict = await self.client_bind.channel_message_create(self.snowflake, content)
        return Message(self.client_bind, **new_message_dict)

    async def post_multi_message_async(self, content: str, break_char: str = '\n',
                                       threshold: int = 1000) -> typing.List[Message]:
        max_length = 2000
        messages = []
        curr_pos = 0
        while len(content) - curr_pos > max_length:
            next_break = content.rfind(break_char, curr_pos, curr_pos + max_length)
            if next_break != -1 and (curr_pos + next_break) > threshold:
                messages.append(await self.post_message_async(content[curr_pos:next_break]))
                curr_pos = next_break
            else:
                messages.append(await self.post_message_async(content[curr_pos:curr_pos + max_length]))
                curr_pos += max_length
        await self.post_message_async(content[curr_pos:])
        return messages

    async def post_file_async(self, file_name: str, file_bytes: bytes) -> Message:
        return Message(self.client_bind,
                       **(await self.client_bind.channel_message_create_file(
                           self.snowflake, file_name, file_bytes))
                       )

    async def message_iter_async_gen(self) -> typing.AsyncGenerator[Message, None]:
        async for message_dict in self.message_dict_iter_async_gen():
            yield (Message(self.client_bind, **message_dict))

    async def message_dict_iter_async_gen(self) -> typing.AsyncGenerator[dict, None]:
        async for message_dict in self.client_bind.channel_message_iter(self.snowflake):
            yield message_dict

    async def get_last_message_async(self) -> Message:
        return Message(self.client_bind,
                       **(await self.client_bind.channel_message_get(self.snowflake, self.last_message_id)))

    async def on_message_created_async_gen(self) -> typing.AsyncGenerator[Message, None]:
        async for message_dict in self.client_bind.event_gen_message_create():
            if message_dict['channel_id'] == self.snowflake:
                yield Message(self.client_bind, **message_dict)
