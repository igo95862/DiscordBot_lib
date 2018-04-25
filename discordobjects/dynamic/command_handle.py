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


def shlex_split(s: str) -> typing.List[str]:
    try:
        return shlex.split(s)
    except ValueError:
        return []


class CommandCallback:

    def __init__(self, message_dict_agen: typing.AsyncGenerator,
                 content_test: typing.Callable[[str], bool],
                 channel_id_test: typing.Callable[[str], bool],
                 user_id_test: typing.Callable[[str], bool],
                 callback: typing.Callable[[typing.Any], typing.Coroutine],
                 parser: typing.Callable[[str], typing.Any] = shlex_split,
                 loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
                 ):
        self.message_dict_agen = message_dict_agen
        self.content_test = content_test
        self.channel_id_test = channel_id_test
        self.user_id_test = user_id_test
        self.parser = parser
        self.event_loop = loop
        self.callback = callback

    async def __call__(self):
        async for message_dict in self.message_dict_agen:
            if not self.channel_id_test(message_dict['channel_id']):
                continue

            if not self.user_id_test(message_dict['channel_id']):
                continue

            if not self.content_test(message_dict['content']):
                continue

            parsed_data = self.parser(message_dict)

            if parsed_data:
                task: asyncio.Task = self.event_loop.create_task(self.callback(parsed_data))
                task.add_done_callback(self._call_back_exception)

    async def _call_back_exception(self, done_task: asyncio.Future):
        exception = done_task.exception()
        if done_task.exception is not None:
            logging.exception(f"Command {repr(self)} raised exception {exception}")
