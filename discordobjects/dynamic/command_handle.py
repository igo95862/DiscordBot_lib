import asyncio
import typing
from collections import OrderedDict
from shlex import split as shelx_split

from ..client import DiscordClientAsync
from ..static import Message

__all__ = ['CommandHandle']


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
                            tokens = shelx_split(message_string)[1:]
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
