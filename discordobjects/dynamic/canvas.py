import asyncio
import typing
from itertools import zip_longest

from ..client import DiscordClientAsync
from ..constants import MESSAGE_MAX_LENGTH
from ..static import GuildTextChannel, Message, User


class Canvas:

    def __init__(
            self, client_bind: DiscordClientAsync, channel_id: str,
            event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
            message_limit: int = 30
    ):
        self.client_bind = client_bind
        self.event_loop = event_loop
        self.owner: User = None
        self.message_limit = message_limit
        self.channel_id = channel_id
        self.channel: GuildTextChannel = None
        self.canvas_messages: typing.List[Message] = None
        self.await_init: asyncio.Future = self.event_loop.create_future()

    async def init_channel(self):
        channel_dict = await self.client_bind.channel_get(self.channel_id)
        self.channel = GuildTextChannel(self.client_bind, **channel_dict)
        self.owner = User(self.client_bind, **(await self.client_bind.me_get()))
        await self.allocate_messages()
        self.await_init.set_result(True)

    async def allocate_messages(self):
        messages: typing.List[Message] = []
        async for m in self.channel.message_iter_async_gen():
            if m.get_author() == self.owner:
                messages.append(m)

            if len(messages) >= self.message_limit:
                break

        # Reverse direction
        self.canvas_messages = list(reversed(messages))

    async def display(self, text_fragments: typing.Iterable[str]):
        current_buffer: typing.List[str] = []
        current_length: int = 0
        message_buffers: typing.List[str] = []

        for line in text_fragments:
            line_length = len(line) + 1  # Account for newline character
            if current_length + line_length > MESSAGE_MAX_LENGTH:
                # Flush buffer
                # TODO: corner case, fragment is more then 2000 in length
                message_buffers.append('\n'.join(current_buffer))
                current_buffer[:] = []
                current_length = 0

            current_buffer.append(line)
            current_length += line_length
        # Flush final buffer
        if current_buffer:
            message_buffers.append('\n'.join(current_buffer))

        new_messages: typing.List[Message] = []
        # Apply the buffers
        for buffer, message in zip_longest(message_buffers, self.canvas_messages):
            # Exhausted message buffers, fill remaining messages with empty
            if buffer is None:
                await message.edit_async('')
                continue

            # Exhausted canvas messages, need to create new messages
            if message is None:
                new_messages.append(await self.channel.post_message_async(buffer))
                continue

            await message.edit_async(buffer)

        # If we created new messages, append them to canvas messages in the end
        if new_messages:
            self.canvas_messages += new_messages

    def __await__(self) -> typing.Awaitable[bool]:
        self.event_loop.create_task(self.init_channel())
        return self.await_init.__await__()
