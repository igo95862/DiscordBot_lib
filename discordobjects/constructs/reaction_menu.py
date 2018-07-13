from functools import partial
from logging import getLogger
from typing import Union, Tuple, Callable, Dict, Awaitable
from asyncio import Future

from ..abstract_objects import AbstractEmoji, AbstractMessage, AbstractGuildMember
from ..util import wrap_if_coroutine

logger = getLogger(__name__)

TypeAction = Callable[[AbstractGuildMember], None]
TypeReaction = Union[AbstractEmoji, str]


class ReactionMenu:

    def __init__(self, message: AbstractMessage, my_user: AbstractGuildMember):
        self.message = message
        self.callback_reaction_add = self.message.event_message_reaction_add.callback_add(
            partial(self._reaction_modify, 'on_switches'))
        self.callback_reaction_remove = self.message.event_message_reaction_remove.callback_add(
            partial(self._reaction_modify, 'off_switches'))
        self.on_switches: Dict[AbstractEmoji, TypeAction] = {}
        self.off_switches: Dict[AbstractEmoji, TypeAction] = {}
        self.event_loop = message.event_message_reaction_add.event_loop
        self.my_user = my_user

    def _reaction_modify(self, attribute_name: str, event_data: Tuple[AbstractEmoji, AbstractGuildMember]):
        emoji, member = event_data
        if member == self.my_user:
            return

        try:
            getattr(self, attribute_name)[emoji](member)
        except KeyError:
            self.event_loop.create_task(self.message.clear_users_reaction_async(member, emoji))

    def add_button(self, emoji: TypeReaction, action: TypeAction):
        action_wrapper = wrap_if_coroutine(self.event_loop, action)
        self.event_loop.create_task(self.message.add_reaction_async(emoji))

        def button_action(member: AbstractGuildMember):
            action_wrapper(member)
            self.event_loop.create_task(self.message.clear_users_reaction_async(member, emoji))

        self.on_switches[emoji] = button_action
        self.off_switches[emoji] = lambda m: m

    def add_switch(self, emoji: TypeReaction, action_on: TypeAction, action_off: TypeAction):
        on_wrapper = wrap_if_coroutine(self.event_loop, action_on)
        off_wrapper = wrap_if_coroutine(self.event_loop, action_off)
        self.event_loop.create_task(self.message.add_reaction_async(emoji))
        self.on_switches[emoji] = on_wrapper
        self.off_switches[emoji] = off_wrapper
