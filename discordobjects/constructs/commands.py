from ..util import EventDispenser
from ..abstract_objects import AbstractMessage, AbstractGuildRole, AbstractUser
from typing import Collection, Callable, List, Dict, Tuple, Any, Optional, Coroutine
from shlex import split as shlex_split
from logging import getLogger
from ..util import wrap_if_coroutine

logger = getLogger(__name__)


TypeAction = Callable[[AbstractMessage, Tuple[Any, ...]], Optional[Coroutine]]


class CommandRealm:

    def __init__(self, message_event: EventDispenser[AbstractMessage],
                 start_pattern: str = '!', help_command: str = 'help',
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

        self.commands_instances: Dict[str, CommandInstance] = {}
        self.start_pattern = start_pattern
        self.help_command = help_command

        self.event_loop = message_event.event_loop

        self.callback_handle = self.message_event.callback_add(self._message_callback)

        self.add_command('help', self.post_help, 'Print the help message')

    async def _message_callback(self, message: AbstractMessage):
        logger.debug(f"Received message {message}")
        if not message.content.startswith(self.start_pattern):
            return
        author_member = message.author_member
        if author_member in self.allowed_users or any((x in author_member for x in self.allowed_roles)):
            try:
                parsed_strings: List[str] = shlex_split(message.content[len(self.start_pattern):])
            except ValueError as e:
                if e.args == ('No closing quotation', ):
                    await message.reply_async('No closing quotation')
                else:
                    await message.reply_async('Unknown parsing error')
                return

            parsed_string_iter = iter(parsed_strings)
            try:
                command_name = next(parsed_string_iter)
            except StopIteration:
                await message.reply_async('No command given')
                return

            try:
                command_instance = self.commands_instances[command_name]
            except KeyError:
                await message.reply_async(
                    f"Command not found. Try **{self.start_pattern} {self.help_command}** for list of commands")
                return

            mentioned_users_iter = iter(message.mentioned_members)

            parsed_values = []
            for s in parsed_string_iter:
                if not s.endswith('>'):
                    parsed_values.append(s)
                    continue

                if (s.startswith('<@') and s[2:-1].isdigit()) or (s.startswith('<@!') and s[3:-1].isdigit()):
                    # User mention no nick
                    parsed_values.append(next(mentioned_users_iter))
                    continue

            command_instance(message, *parsed_values)

    def add_command(self, command_name: str, action: TypeAction, description: str):
        self.commands_instances[command_name] = CommandInstance(action, description, self)

    async def post_help(self, message: AbstractMessage, *_):
        await message.reply_multiple_async(self.help_message)

    @property
    def help_message(self) -> str:
        descriptions = '\n'.join((f"**{k}**\t{v.description}" for k, v in self.commands_instances.items()))
        return f"Available commands: \n{descriptions}"


class CommandInstance:

    def __init__(self, action: TypeAction, description: str, parent_realm: CommandRealm):
        self.parent_realm = parent_realm
        self.action = wrap_if_coroutine(parent_realm.event_loop, action)
        self.description = description

    def __call__(self, *args, **kwargs):
        self.action(*args, **kwargs)




