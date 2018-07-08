from discordobjects.abstract_objects import AbstractUser
from ..client import DiscordClientAsync
from typing import Dict, List, Mapping, Union, Iterator, Tuple, AsyncGenerator, Type, Callable, Collection, Optional
from pprint import pprint
from asyncio import Future, AbstractEventLoop
from ..util import EventDispenser
from ..abstract_objects import (
    AbstractGuildMember, AbstractGuild, AbstractGuildChannelText, AbstractMessage, AbstractEmoji)
from ..static_objects import StaticDmChannel, StaticMessage, StaticUser, StaticEmoji
from collections.abc import Mapping as AbcMapping
from weakref import ref as weak_ref, WeakValueDictionary
from functools import partial


class SubclassedDict(dict):
    # HACK: allows to weak referencing the dictionary
    pass


class GuildUnit(AbstractGuild):

    @property
    def roles(self) -> Mapping[str, 'LinkedRole']:
        return self._roles_mapping

    @property
    def members(self) -> Mapping[str, 'LinkedMember']:
        return self._members_mapping

    @property
    def channels(self) -> Mapping[str, 'LinkedGuildChannelText']:
        return self._channels_mapping

    @property
    def snowflake(self) -> str:
        return self._guild_id

    @property
    def client_bind(self) -> DiscordClientAsync:
        return self._client_bind

    def __init__(self, client: DiscordClientAsync, guild_id: str, event_loop: AbstractEventLoop):
        self._client_bind = client
        self._guild_id = guild_id
        self.event_loop = event_loop

        self._my_user_id = None

        self._members_data: Dict[str, Dict] = {}
        self._roles_data: Dict[str, Dict] = {}
        self._channels_data: Dict[str, Dict] = {}
        self._voice_states_data: Dict[str, Dict] = {}
        self._guild_data: Dict[str, Dict] = {}
        self._message_data: Dict[str, WeakValueDictionary[SubclassedDict]] = {}
        self.is_initialized: Future = Future(loop=event_loop)

        # Callbacks
        self.callback_ready = self.client_bind.event_ready.callback_add(self._on_ready)
        self.callback_guild_create = self.client_bind.event_guild_create.callback_add(self._on_guild_create)
        self.callback_guild_member_add = self.client_bind.event_guild_member_add.callback_add(self._on_guild_member_add)
        self.callback_message_reaction_add = self.client_bind.event_message_reaction_add.callback_add(
            partial(self._on_message_reaction_modify, 'event_emoji_add'))
        self.callback_message_reaction_remove = self.client_bind.event_message_reaction_remove.callback_add(
            partial(self._on_message_reaction_modify, 'event_emoji_remove'))

        # Events
        self.event_member_joined = EventDispenser(event_loop)
        self.event_member_update = EventDispenser(event_loop)
        self.event_member_removed = EventDispenser(event_loop)
        self._event_channel_message_create: Dict[str, Callable[[], EventDispenser]] = {}

        # Mappings
        class MemberMapping(AbcMapping):

            def __getitem__(_, key: Union[str, AbstractGuildMember]) -> 'LinkedMember':
                if isinstance(key, str):
                    user_id = key
                elif isinstance(key, AbstractGuildMember):
                    user_id = key.snowflake
                else:
                    raise TypeError(f"Expected str, AbstractGuildMember got {key.__class__}")

                return LinkedMember(self, user_id)

            def __len__(_) -> int:
                return len(self._members_data)

            def __iter__(_) -> Iterator['LinkedMember']:
                return iter((LinkedMember(self, value['user']['id']) for value in self._members_data.values()))

        self._members_mapping = MemberMapping()

        class RolesMapping(AbcMapping):
            def __getitem__(_, k: str) -> LinkedRole:
                return LinkedRole(self, k)

            def __len__(_) -> int:
                return len(self.roles)

            def __iter__(_) -> Iterator[LinkedRole]:
                return iter((LinkedRole(self, x['id']) for x in self._roles_data.values()))

        self._roles_mapping = RolesMapping()

        class ChannelsMapping(AbcMapping):
            def __getitem__(_, k: str) -> LinkedGuildChannelText:
                return LinkedGuildChannelText(self, k)

            def __len__(_) -> int:
                return len(self._channels_data)

            def __iter__(_) -> Iterator[LinkedGuildChannelText]:
                return iter((LinkedGuildChannelText(self, k['id']) for k in self._channels_data.values()))

        self._channels_mapping = ChannelsMapping()

    def _on_ready(self, event_data: Dict):
        self._my_user_id = event_data['user']['id']

    def _on_message_reaction_modify(self, attribute_name: str, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id != self.snowflake:
            return

        channel_id = event_data['channel_id']
        message_id = event_data['message_id']
        try:
            message_data = self._message_data[channel_id][message_id]
        except KeyError:
            return

        emoji = StaticEmoji(**event_data['emoji'])

        try:
            event_dispenser: EventDispenser = getattr(message_data, attribute_name)
        except AttributeError:
            return

        event_dispenser.put((emoji, self.members[event_data['user_id']]))

    def _on_guild_member_add(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            user_id = event_data['user']['id']
            self._members_data[user_id] = event_data
            self.event_member_joined.put(LinkedMember(self, user_id))

    def _on_guild_member_update(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            user_id = event_data['user']['id']
            member_dict = self._members_data[user_id]
            member_dict['roles'] = event_data['roles']
            member_dict['user'] = event_data['user']
            member_dict['nick'] = event_data['nick']
            self.event_member_update.put(LinkedMember(self, user_id))

    def _on_guild_member_remove(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            user_id = event_data['user']['id']
            self._members_data.pop(user_id)
            self.event_member_removed.put(LinkedMember(self, user_id))

    def _on_guild_create(self, event_data: Dict):
        if event_data['id'] == self._guild_id:
            roles_data = event_data.pop('roles')
            channels_data = event_data.pop('channels')
            members_data = event_data.pop('members')
            voice_states_data = event_data.pop('voice_states')
            self._populate_channels(roles_data)
            self._populate_channels(channels_data)
            self._populate_members(members_data)
            self._populate_voice_states(voice_states_data)
            self._guild_data = event_data
            self.is_initialized.set_result(True)

    def _populate_channels(self, channel_list: List[Dict]):
        self._channels_data = {x['id']: x for x in channel_list}

    def _populate_members(self, members_list: List[Dict]):
        self._members_data = {x['user']['id']: x for x in members_list}

    def _populate_roles(self, roles_list: List[Dict]):
        self._roles_data = {x['id']: x for x in roles_list}

    def _populate_voice_states(self, voice_states_list: List[Dict]):
        self._voice_states_data = {x['user_id']: x for x in voice_states_list}

    def _add_linked_message_data(self, channel_id: str, message_dict: dict) -> SubclassedDict:
        message_id = message_dict['id']
        try:
            channel_messages_data = self._message_data[channel_id]
        except KeyError:
            channel_messages_data = WeakValueDictionary()
            self._message_data[channel_id] = channel_messages_data

        message_data = SubclassedDict(message_dict)
        channel_messages_data[message_id] = message_data
        return message_data

    async def reload(self):
        pass

    def __await__(self):
        return self.is_initialized.__await__()

    @property
    def my_member(self) -> 'LinkedMember':
        return self.members[self._my_user_id]


class BaseLinked:
    def __init__(self, parent_unit: GuildUnit):
        self.parent_unit = parent_unit


class LinkedMember(BaseLinked, AbstractGuildMember):
    @property
    def username(self) -> str:
        return self.parent_unit._members_data[self._member_id]['user']['username']

    @property
    def discriminator(self) -> str:
        return self.parent_unit._members_data[self._member_id]['user']['username']

    @property
    def avatar_hash(self) -> str:
        return self.parent_unit._members_data[self._member_id]['user']['avatar']

    async def dm_open_async(self) -> StaticDmChannel:
        return await StaticDmChannel.load_async(self.client_bind, self._member_id)

    @property
    def snowflake(self) -> str:
        return self._member_id

    @property
    def client_bind(self) -> DiscordClientAsync:
        return self.parent_unit.client_bind

    def __init__(self, parent_unit: GuildUnit, member_id: str):
        self._member_id = member_id
        super().__init__(parent_unit)


class LinkedRole(BaseLinked):
    def __init__(self, parent_unit: GuildUnit, role_id: str):
        self.role_id = role_id
        super().__init__(parent_unit)


class LinkedGuildChannelText(BaseLinked, AbstractGuildChannelText):
    @property
    def event_message_created(self) -> EventDispenser[StaticMessage]:
        try:
            old_dispenser = self.parent_unit._event_channel_message_create[self.snowflake]()
            return old_dispenser
        except KeyError:
            pass

        new_dispenser = EventDispenser(self.parent_unit.event_loop)

        def clean_up():
            self.parent_unit._event_channel_message_create.pop(self.snowflake)

        def new_hook(message_dict: dict):
            if message_dict['channel_id'] == self.snowflake:
                '''
                message_id = message_dict['id']
                try:
                    channel_messages_data = self.parent_unit._message_data[self.snowflake]
                except KeyError:
                    channel_messages_data = WeakValueDictionary()
                    self.parent_unit._message_data[self.snowflake] = channel_messages_data

                message_data = SubclassedDict(message_dict)
                channel_messages_data[message_id] = message_data
                '''
                message_data = self.parent_unit._add_linked_message_data(self.snowflake, message_dict)
                new_dispenser.put(LinkedMessage(self, message_data))

        new_dispenser.hook = new_hook
        self.client_bind.event_message_create.callback_add(new_hook)
        self.parent_unit._event_channel_message_create[self.snowflake] = weak_ref(new_dispenser, clean_up)
        return new_dispenser

    @property
    def message_class(self) -> Type['LinkedMessage']:
        return LinkedMessage

    async def get_last_message(self):
        raise NotImplementedError

    async def message_iter_async_gen(self) -> AsyncGenerator['StaticMessage', None]:
        raise NotImplementedError

    async def post_single_message_async(self, content: str, files: Tuple[str, bytes] = None) -> 'LinkedMessage':
        message_dict = await self.client_bind.channel_message_create(self.snowflake, content)
        message_data = self.parent_unit._add_linked_message_data(self.snowflake, message_dict)
        return LinkedMessage(self, message_data)

    @property
    def type_int(self) -> int:
        raise NotImplementedError

    @property
    def snowflake(self) -> str:
        return self.channel_id

    @property
    def client_bind(self) -> DiscordClientAsync:
        return self.parent_unit.client_bind

    def __init__(self, parent_unit: GuildUnit, channel_id: str):
        self.channel_id = channel_id
        super().__init__(parent_unit)


class LinkedMessage(AbstractMessage):
    def __init__(self, parent_channel: LinkedGuildChannelText, message_data: SubclassedDict):
        self._parent_channel = parent_channel
        self._message_data = message_data
        self._client_bind = parent_channel.client_bind
    
    @property
    def content(self) -> str:
        return self._message_data['content']

    @property
    def author_user(self) -> StaticUser:
        return StaticUser(self._parent_channel.client_bind, **self._message_data)

    @property
    def author_member(self) -> AbstractUser:
        author_id = self._message_data['author']['id']
        return self._parent_channel.parent_unit.members[author_id]

    @property
    def parent_channel_id(self) -> str:
        return self._parent_channel.snowflake

    async def edit_async(self, new_content: str) -> 'LinkedMessage':
        await self.client_bind.channel_message_edit(self.parent_channel_id, self.snowflake, new_content)
        # TODO: Synchronise with socket events
        return self

    @property
    def mentioned_users(self) -> Collection['StaticUser']:
        return [StaticUser(self.client_bind, **x) for x in self._message_data['mentions']]

    @property
    def mentioned_members(self) -> Collection['LinkedMember']:
        return [self._parent_channel.parent_unit.members[x['id']] for x in self._message_data['mentions']]

    @property
    def snowflake(self) -> str:
        return self._message_data['id']

    @property
    def client_bind(self) -> DiscordClientAsync:
        return self._client_bind

    @property
    def event_message_reaction_add(self) -> EventDispenser[Tuple[LinkedMember, StaticEmoji]]:
        try:
            return self._message_data.event_emoji_add
        except AttributeError:
            new_dispenser = EventDispenser(self._parent_channel.parent_unit.event_loop)
            self._message_data.event_emoji_add = new_dispenser
            return new_dispenser

    @property
    def event_message_reaction_remove(self) -> EventDispenser[Tuple[LinkedMember, StaticEmoji]]:
        try:
            return self._message_data.event_emoji_remove
        except AttributeError:
            new_dispenser = EventDispenser(self._parent_channel.parent_unit.event_loop)
            self._message_data.event_emoji_remove = new_dispenser
            return new_dispenser





