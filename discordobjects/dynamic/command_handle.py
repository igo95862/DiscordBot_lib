import asyncio
import typing
import logging
from collections import OrderedDict
import shlex

from ..client import DiscordClientAsync
from ..static import Message

__all__ = ['CommandHandle', 'CommandCallback']


class CommandHandle:

    def __init__(self, client_bind: DiscordClientAsync,
                 command_start_pattern: str,
                 test_channel_id: typing.Callable[[str], bool],
                 test_user_id: typing.Callable[[str], bool],
                 loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.client_bind = client_bind
        self.command_start_pattern = command_start_pattern
        self.test_channel_id = test_channel_id
        self.test_user_id = test_user_id
        self.loop = loop

    async def __call__(self) -> typing.AsyncGenerator[typing.Tuple[OrderedDict, Message], None]:
        async for message_dict in self.client_bind.event_gen_message_create():
            if self.test_channel_id(message_dict['channel_id']):
                if self.test_user_id(message_dict['author']['id']):
                    message_string: str = message_dict['content']
                    if message_string.startswith(self.command_start_pattern):
                        try:
                            tokens = shlex.split(message_string)[1:]
                        except ValueError:
                            continue

                        # send tokens in to dicts
                        current_key = 'default'
                        args_dict = OrderedDict({current_key: []})
                        for t in tokens:
                            if t.startswith('--'):
                                current_key = t
                                if current_key not in args_dict.keys():
                                    args_dict[current_key] = []
                                continue
                            args_dict[current_key].append(t)

                        yield (args_dict, Message(self.client_bind, **message_dict))


def parser_shlex_split_and_message(message_dict: dict, client_bind: DiscordClientAsync
                                   ) -> typing.Tuple[typing.List, Message]:
    try:
        content_split = shlex.split(message_dict['content'])
    except ValueError:
        content_split = []

    return content_split, Message(client_bind, **message_dict)


class CommandCallback:

    def __init__(self, client_bind: DiscordClientAsync,
                 content_test: typing.Callable[[str], bool],
                 channel_id_test: typing.Callable[[str], bool],
                 user_id_test: typing.Callable[[str], bool],
                 callback: typing.Callable[[typing.Any], typing.Coroutine],
                 parser: typing.Callable[[dict, DiscordClientAsync], typing.Any] = parser_shlex_split_and_message,
                 loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
                 ):
        self.client_bind = client_bind
        self.content_test = content_test
        self.channel_id_test = channel_id_test
        self.user_id_test = user_id_test
        self.parser = parser
        self.event_loop = loop
        self.callback = callback

    async def __call__(self):
        async for message_dict in self.client_bind.event_gen_message_create():

            async def command():
                if not self.channel_id_test(message_dict['channel_id']):
                    return

                if not self.content_test(message_dict['content']):
                    return

                if not self.user_id_test(message_dict['author']['id']):
                    return

                parsed_data = self.parser(message_dict, self.client_bind)
                await self.callback(*parsed_data)

            task: asyncio.Task = self.event_loop.create_task(command())
            task.add_done_callback(self._call_back_exception)

    def _call_back_exception(self, done_task: asyncio.Future):
        exception = done_task.exception()
        if exception is not None:
            logging.exception(f"Command {repr(self)} raised exception {repr(exception)}")
