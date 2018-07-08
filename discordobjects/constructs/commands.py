from ..util import EventDispenser
from ..abstract_objects import AbstractMessage, AbstractGuildRole, AbstractUser
from typing import Collection, Sequence, Callable, List
from shlex import split as shlex_split
from logging import getLogger
from itertools import takewhile

logger = getLogger(__name__)


class CommandRealm:

    def __init__(self, message_event: EventDispenser[AbstractMessage],
                 start_pattern: str = '!',
                 allowed_roles: Collection[AbstractGuildRole] = None, allowed_users: Collection[AbstractUser] = None):
        self.message_event = message_event
        if allowed_roles is None:
            self.allowed_roles = []
        else:
            self.allowed_roles = allowed_roles

        if allowed_users is None:
            self.allowed_users = []
        else:
            self.allowed_users = allowed_users

        self.commands_patterns: List[CommandPattern] = []
        self.start_pattern = start_pattern

        self.callback_handle = self.message_event.callback_add(self._message_callback)

    async def _message_callback(self, message: AbstractMessage):
        logger.debug(f"Received message {message}")
        author_member = message.author_member
        if author_member in self.allowed_users or any((x in author_member for x in self.allowed_roles)):
            try:
                parsed_strings: List[str] = shlex_split(message.content[len(self.start_pattern):])
            except ValueError as e:
                await message.reply_async(str(e))
                return

            mentioned_users_iter = iter(message.mentioned_members)
            parsed_values = []
            for s in parsed_strings:
                if s.startswith('<@') and s.endswith('>'):
                    parsed_values.append(next(mentioned_users_iter))
                else:
                    parsed_values.append(s)

            print(parsed_values)
            for c in self.commands_patterns:
                if c == parsed_values:
                    c(message, *parsed_values)
                    return

    def add_command(self, command_pattern: Sequence, action: Callable, description: str):
        self.commands_patterns.append(CommandPattern(command_pattern, action, description))


class CommandPattern:

    def __init__(self, command_pattern: Sequence, action: Callable, description: str):
        self.command_pattern = command_pattern
        self.action = action
        self.description = description

    def __eq__(self, other: List):
        other_iter = iter(other)
        other_running = True
        inner_iter = iter(self.command_pattern)
        inner_running = True

        while other_running and inner_running:
            try:
                other_next = next(other_iter)
            except StopIteration:
                other_running = False

            try:
                inner_next = next(inner_iter)
            except StopIteration:
                other_running = False

            if isinstance(other_next, str):
                if other_next != inner_next:
                    return False
            elif isinstance(other_next, AbstractUser) and isinstance(inner_next, UserTarget):
                continue
            else:
                return False
        return True

    def __call__(self, *args, **kwargs):
        self.action(*args, **kwargs)

class UserTarget:
    pass



