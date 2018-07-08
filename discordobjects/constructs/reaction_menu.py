from ..dynamic.guild_unit import LinkedMessage, LinkedMember
from ..abstract_objects import AbstractEmoji
from typing import Collection, Union, Tuple, Callable, Dict
from ..util import wrap_if_coroutine
from logging import getLogger
from functools import partial

logger = getLogger(__name__)


ActionType = Callable[[LinkedMember], None]


class ReactionMenu:

    def __init__(self, message: LinkedMessage, my_user: LinkedMember):
        self.message = message
        self.callback_reaction_add = self.message.event_message_reaction_add.callback_add(
            partial(self._reaction_modify, 'on_switches'))
        self.callback_reaction_remove = self.message.event_message_reaction_remove.callback_add(
            partial(self._reaction_modify, 'off_switches'))
        self.on_switches: Dict[AbstractEmoji, ActionType] = {}
        self.off_switches: Dict[AbstractEmoji, ActionType] = {}
        self.event_loop = message.event_message_reaction_add.event_loop
        self.my_user = my_user

    def _reaction_modify(self, attribute_name: str, event_data: Tuple[AbstractEmoji, LinkedMember]):
        emoji, member = event_data
        if member == self.my_user:
            return

        try:
            getattr(self, attribute_name)[emoji](member)
        except KeyError:
            self.event_loop.create_task(self.message.clear_users_reaction_async(member, emoji))

    def add_button(self, emoji: Union[AbstractEmoji, str], action: ActionType):
        action_wrapper = wrap_if_coroutine(self.event_loop, action)
        self.event_loop.create_task(self.message.add_reaction_async(emoji))

        def button_action(member: LinkedMember):
            action_wrapper(member)
            self.event_loop.create_task(self.message.clear_users_reaction_async(member, emoji))

        self.on_switches[emoji] = button_action
        self.off_switches[emoji] = lambda m: m

    def add_switch(self, emoji: Union[AbstractEmoji, str], action_on: ActionType, action_off: ActionType):
        on_wrapper = wrap_if_coroutine(self.event_loop, action_on)
        off_wrapper = wrap_if_coroutine(self.event_loop, action_off)
        self.event_loop.create_task(self.message.add_reaction_async(emoji))
        self.on_switches[emoji] = on_wrapper
        self.off_switches[emoji] = off_wrapper
