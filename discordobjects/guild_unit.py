from asyncio import Future, AbstractEventLoop
from functools import partial
from logging import getLogger
from typing import (Dict, List, Mapping, Union, Iterator, Tuple, AsyncGenerator, Type, Callable, Collection, Optional,
                    Iterable, TypeVar, Generic)
from weakref import ref as weak_ref, WeakValueDictionary

from collections.abc import Mapping as AbcMapping, Iterable as AbcIterable

from discordobjects.abstract_objects import AbstractUser
from discordobjects.abstract_objects import (
    AbstractGuildMember, AbstractGuild, AbstractGuildChannelText, AbstractGuildChannel, AbstractMessage, AbstractEmoji,
    AbstractGuildRole)
from discordobjects.client import DiscordClientAsync
from discordobjects.static_objects import StaticDmChannel, StaticMessage, StaticUser, StaticEmoji
from discordobjects.util import EventDispenser, SubclassedDict

logger = getLogger(__name__)


class DataDict(SubclassedDict):
    def __init__(self, *args, **kwargs):
        self.is_alive = True
        super().__init__(*args, **kwargs)


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
    def emojis(self) -> Mapping[str, 'LinkedEmoji']:
        return self._emojis_mapping

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

        self._members_data: Dict[str, DataDict] = {}
        self._roles_data: Dict[str, DataDict] = {}
        self._channels_data: Dict[str, DataDict] = {}
        self._voice_states_data: Dict[str, Dict] = {}
        self._guild_data: Dict[str, Dict] = {}
        self._emoji_data: Dict[str, DataDict] = {}
        self._message_data: Dict[str, WeakValueDictionary[SubclassedDict]] = {}
        self.is_initialized: Future = Future(loop=event_loop)

        # Callbacks
        self.callback_ready = self.client_bind.event_ready.callback_add(self._on_ready)
        self.callback_guild_create = self.client_bind.event_guild_create.callback_add(self._on_guild_create)
        # Member Callbacks
        self.callback_member_add = self.client_bind.event_guild_member_add.callback_add(self._on_member_add)
        self.callback_member_modify = self.client_bind.event_guild_member_update.callback_add(self._on_member_update)
        # Roles callbacks
        self.callback_role_create = self.client_bind.event_guild_role_create.callback_add(self._on_role_create)
        self.callback_role_update = self.client_bind.event_guild_role_update.callback_add(self._on_role_update)
        self.callback_role_delete = self.client_bind.event_guild_role_delete.callback_add(self._on_role_remove)
        # Emoji callbacks
        self.callback_emojies_update = self.client_bind.event_guild_emoji_update.callback_add(self._on_emojies_update)

        self.callback_message_reaction_add = self.client_bind.event_message_reaction_add.callback_add(
            partial(self._on_message_reaction_modify, 'event_reaction_add'))
        self.callback_message_reaction_remove = self.client_bind.event_message_reaction_remove.callback_add(
            partial(self._on_message_reaction_modify, 'event_reaction_remove'))

        # Events
        self.event_member_joined: EventDispenser[LinkedMember] = EventDispenser(event_loop)
        self.event_member_update = EventDispenser(event_loop)
        self.event_member_removed = EventDispenser(event_loop)
        self._event_channel_message_create: Dict[str, Callable[[], EventDispenser]] = {}
        self._on_member_roles_modify: EventDispenser = None

        # Mappings
        self._members_mapping = MemberMapping(self)
        self._roles_mapping = RolesMapping(self)
        self._channels_mapping = ChannelsMappingText(self)
        self._emojis_mapping = EmojisMapping(self)

        # Caches
        self._roles_cache = WeakValueDictionary()
        self._channels_cache = WeakValueDictionary()
        self._members_cache = WeakValueDictionary()

    def _on_ready(self, event_data: Dict):
        self._my_user_id = event_data['user']['id']

    def _on_message_reaction_modify(self, key_name: str, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id != self.snowflake:
            return

        if event_data['user_id'] == self._my_user_id:
            return

        channel_id = event_data['channel_id']
        message_id = event_data['message_id']
        try:
            message_data = self._message_data[channel_id][message_id]
        except KeyError:
            return

        try:
            event_dispenser: EventDispenser = message_data[key_name]
        except KeyError:
            return

        emoji = StaticEmoji(**event_data['emoji'])
        event_dispenser.put((emoji, self.members[event_data['user_id']]))

    # region Member events callbacks
    def _on_member_add(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            user_id = event_data['user']['id']
            self._members_data[user_id] = DataDict(event_data)
            self.event_member_joined.put(LinkedMember(self, user_id))

    def _on_member_update(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            user_id = event_data['user']['id']
            member_dict = self._members_data[user_id]
            old_roles_ids_list = member_dict['roles']
            new_roles_ids_list = event_data['roles']
            member_dict['roles'] = new_roles_ids_list
            member_dict['user'] = event_data['user']
            member_dict['nick'] = event_data['nick']
            self.event_member_update.put(LinkedMember(self, user_id))

            if self._on_member_roles_modify is not None:
                old_roles_ids_set = set(old_roles_ids_list)
                new_roles_ids_set = set(new_roles_ids_list)
                self._on_member_roles_modify.put(
                    (self.members[user_id],
                     tuple((self.roles[x] for x in new_roles_ids_set - old_roles_ids_set)),
                     tuple((self.roles[x] for x in old_roles_ids_set - new_roles_ids_set ))))

    def _on_member_remove(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            user_id = event_data['user']['id']
            self._members_data.pop(user_id)
            self.event_member_removed.put(LinkedMember(self, user_id))

    # endregion

    # region Role callbacks
    def _on_role_create(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            role_id = event_data['role']['id']
            role_data = DataDict(event_data['role'])
            self._roles_data[role_id] = role_data

    def _on_role_update(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            role_id = event_data['role']['id']
            self._roles_data[role_id].update(event_data['role'])



    def _on_role_remove(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self._guild_id:
            role_data = self._roles_data.pop(event_data['role_id'])

    # endregion

    def _on_emojies_update(self, event_data: Dict):
        if event_data['guild_id'] == self._guild_id:
            updated_emojies = event_data['emojis']
            updated_ids = {x['id'] for x in updated_emojies}
            old_ids = set(self._emoji_data.keys())
            removed_ids = old_ids - updated_ids

            for new_emoji_dict in updated_emojies:
                emoji_id = new_emoji_dict['id']
                try:
                    self._emoji_data[emoji_id].update(new_emoji_dict)
                except KeyError:
                    self._emoji_data[emoji_id] = DataDict(new_emoji_dict)

            for x in removed_ids:
                self._emoji_data.pop(x)

    def _on_guild_create(self, event_data: Dict):
        if event_data['id'] == self._guild_id:
            roles_data = event_data.pop('roles')
            channels_data = event_data.pop('channels')
            members_data = event_data.pop('members')
            voice_states_data = event_data.pop('voice_states')
            emoji_data = event_data.pop('emojis')
            self._populate_roles(roles_data)
            self._populate_channels(channels_data)
            self._populate_members(members_data)
            self._populate_voice_states(voice_states_data)
            self._populate_emoji(emoji_data)
            self._guild_data = event_data
            self.is_initialized.set_result(True)

    def _populate_channels(self, channel_list: List[Dict]):
        self._channels_data = {x['id']: DataDict(x) for x in channel_list}

    def _populate_members(self, members_list: List[Dict]):
        self._members_data = {x['user']['id']: DataDict(x) for x in members_list}

    def _populate_roles(self, roles_list: List[Dict]):
        self._roles_data = {x['id']: DataDict(x) for x in roles_list}

    def _populate_voice_states(self, voice_states_list: List[Dict]):
        self._voice_states_data = {x['user_id']: x for x in voice_states_list}

    def _populate_emoji(self, emoji_list: List[Dict]):
        self._emoji_data = {x['id']: DataDict(x) for x in emoji_list}

    def _add_linked_message_data(self, channel_id: str, message_dict: dict) -> DataDict:
        message_id = message_dict['id']
        try:
            channel_messages_data = self._message_data[channel_id]
        except KeyError:
            channel_messages_data = WeakValueDictionary()
            self._message_data[channel_id] = channel_messages_data

        message_data = DataDict(message_dict)
        channel_messages_data[message_id] = message_data
        return message_data

    async def reload(self):
        raise NotImplementedError

    @property
    def on_member_roles_modify(self) -> EventDispenser[Tuple['LinkedMember',
                                                             Tuple['LinkedRole', ...],
                                                             Tuple['LinkedRole', ...]]]:
        if self._on_member_roles_modify is None:
            new_dispencer = EventDispenser(self.event_loop)
            self._on_member_roles_modify = new_dispencer
            return new_dispencer
        else:
            return self._on_member_roles_modify

    def __await__(self):
        return self.is_initialized.__await__()

    @property
    def my_member(self) -> 'LinkedMember':
        return self.members[self._my_user_id]

    def __contains__(self, item: AbstractUser):
        return item.snowflake in self._members_data


class MemberMapping(AbcMapping):
    def __init__(self, parent_unit: GuildUnit):
        self.parent = parent_unit

    def __getitem__(self, key: Union[str, AbstractGuildMember]) -> 'LinkedMember':
        if isinstance(key, str):
            user_id = key
        elif isinstance(key, AbstractUser):
            user_id = key.snowflake
        else:
            raise TypeError(f"Expected str, AbstractGuildMember got {key.__class__}")

        return LinkedMember(self.parent, user_id)

    def __len__(self) -> int:
        return len(self.parent._members_data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.parent._members_data)


class RolesMapping(AbcMapping):
    def __init__(self, parent_unit: GuildUnit):
        self.parent = parent_unit

    def __getitem__(self, k: str) -> 'LinkedRole':
        try:
            return self.parent._roles_cache[k]
        except KeyError:
            new_linked_role = LinkedRole(self.parent, k)
            self.parent._roles_cache[k] = new_linked_role
            return new_linked_role

    def __len__(self) -> int:
        return len(self.parent._roles_data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.parent._roles_data)

TypeMappingGeneric = Generic('TypeMappingGeneric')

class ChannelsMappingAbstract(AbcMapping):
    def __init__(self, parent_unit: GuildUnit, channel_class: Type[TypeMappingGeneric]):
        self.parent = parent_unit
        self.channel_class = channel_class

    def __getitem__(self, k: str) -> TypeMappingGeneric:
        return self.channel_class(self.parent, k)

    def __len__(self) -> int:
        return len(self.parent._channels_data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.parent._channels_data)


class ChannelsMappingText(ChannelsMappingAbstract):

    def __init__(self, parent_unit: GuildUnit):
        super().__init__(parent_unit, LinkedGuildChannelText)





class EmojisMapping(AbcMapping):
    def __init__(self, parent_unit: GuildUnit):
        self.parent = parent_unit

    def __getitem__(self, k: str) -> 'LinkedEmoji':
        return LinkedEmoji(self.parent, self.parent._emoji_data[k])

    def __len__(self) -> int:
        return len(self.parent._emoji_data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.parent._emoji_data)


class BaseLinked:
    def __init__(self, parent_unit: GuildUnit):
        self.parent_unit = parent_unit


class LinkedMember(BaseLinked, AbstractGuildMember):
    @property
    def role_ids(self) -> List[str]:
        return self._member_data['roles']

    @property
    def username(self) -> str:
        return self._member_data['user']['username']

    @property
    def discriminator(self) -> str:
        return self._member_data['user']['discriminator']

    @property
    def avatar_hash(self) -> str:
        return self._member_data['user']['avatar']

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
        self._member_data = parent_unit._members_data[member_id]
        super().__init__(parent_unit)
        self._role_iterable = RolesIterable(self)

    @property
    def roles(self):
        return self._role_iterable

    async def roles_modify_async(
            self, *args, add_roles: Iterable[Union[str, AbstractGuildRole]] = None,
            subtract_roles: Iterable[Union[str, AbstractGuildRole]] = None):
        if args:
            raise TypeError('Use key value arguments')
        if add_roles is not None:
            add_roles_set = {x.snowflake if isinstance(x, AbstractGuildRole) else x for x in add_roles}
        else:
            add_roles_set = set()

        if subtract_roles is not None:
            subtract_roles_set = {x.snowflake if isinstance(x, AbstractGuildRole) else x for x in subtract_roles}
        else:
            subtract_roles_set = set()

        current_roles_set = set(self.role_ids)
        new_roles = list(current_roles_set - subtract_roles_set | add_roles_set)
        await self.client_bind.guild_member_modify(self.parent_unit.snowflake, self.snowflake, new_roles=new_roles)


class RolesIterable(AbcIterable):
    def __init__(self, parent: LinkedMember):
        self.parent = parent

    def __iter__(self) -> Iterator['LinkedRole']:
        for role_id in self.parent.role_ids:
            yield self.parent.parent_unit.roles[role_id]


class LinkedRole(BaseLinked, AbstractGuildRole):
    @property
    def role_name(self) -> str:
        return self._role_data['name']

    @property
    def role_color(self) -> int:
        return self._role_data['color']

    @property
    def display_separately(self) -> bool:
        return self._role_data['mentionable']

    @property
    def position(self) -> int:
        return self._role_data['position']

    @property
    def permissions_int(self) -> int:
        return self._role_data['permissions']

    @property
    def is_managed(self) -> bool:
        return self._role_data['managed']

    @property
    def is_mentionable(self) -> bool:
        return self._role_data['mentionable']

    @property
    def parent_guild_id(self) -> str:
        return self.parent_unit.snowflake

    @property
    def snowflake(self) -> str:
        return self.role_id

    @property
    def client_bind(self) -> DiscordClientAsync:
        return self.parent_unit.client_bind

    def __init__(self, parent_unit: GuildUnit, role_id: str):
        self.role_id = role_id
        self._role_data = parent_unit._roles_data[role_id]
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

    async def message_iter_async_gen(self) -> AsyncGenerator['LinkedMessage', None]:
        async for message_dict in self.client_bind.channel_message_iter(self.snowflake):
            yield LinkedMessage(self, self.parent_unit._add_linked_message_data(self.snowflake, message_dict))

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
        self._channel_data = parent_unit._channels_data[channel_id]
        super().__init__(parent_unit)

    async def load_message_async(self, message_id: str):
        message_dict = await self.client_bind.channel_message_get(self.snowflake, message_id)
        message_data = self.parent_unit._add_linked_message_data(self.snowflake, message_dict)
        return LinkedMessage(self, message_data)


class LinkedMessage(AbstractMessage):
    async def reply_async(self, content: str) -> 'LinkedMessage':
        return await self._parent_channel.post_single_message_async(content)

    def __init__(self, parent_channel: LinkedGuildChannelText, message_data: DataDict):
        self._parent_channel = parent_channel
        self._message_data = message_data
        self._client_bind = parent_channel.client_bind
        self._event_reaction_add = None
        self._event_reaction_add_cb = None
        self._event_reaction_remove = None
        self._event_reaction_remove_cb = None

    @property
    def content(self) -> str:
        return self._message_data['content']

    @property
    def author_user(self) -> StaticUser:
        return StaticUser(self._parent_channel.client_bind, **self._message_data)

    @property
    def author_member(self) -> LinkedMember:
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
    def event_message_reaction_add(self) -> EventDispenser[Tuple[StaticEmoji, LinkedMember]]:
        if self._event_reaction_add is None:
            self._event_reaction_add = EventDispenser(self.client_bind.event_loop)

            def reaction_hook(event_data: Dict):
                channel_id = event_data['channel_id']
                if channel_id != self.parent_channel_id:
                    return

                message_id = event_data['message_id']
                if message_id != self.snowflake:
                    return

                if event_data['user_id'] == self._parent_channel.parent_unit._my_user_id:
                    return

                emoji = StaticEmoji(**event_data['emoji'])
                self._event_reaction_add.put((emoji, self._parent_channel.parent_unit.members[event_data['user_id']]))

            self._event_reaction_add_cb = self.client_bind.event_message_reaction_add.callback_add(reaction_hook)

        return self._event_reaction_add

    @property
    def event_message_reaction_remove(self) -> EventDispenser[Tuple[StaticEmoji, LinkedMember]]:
        if self._event_reaction_remove is None:
            self._event_reaction_remove = EventDispenser(self.client_bind.event_loop)

            def reaction_hook(event_data: Dict):
                channel_id = event_data['channel_id']
                if channel_id != self.parent_channel_id:
                    return

                message_id = event_data['message_id']
                if message_id != self.snowflake:
                    return

                if event_data['user_id'] == self._parent_channel.parent_unit._my_user_id:
                    return

                emoji = StaticEmoji(**event_data['emoji'])
                self._event_reaction_remove.put((emoji, self._parent_channel.parent_unit.members[event_data['user_id']]))

            self._event_reaction_remove_cb = self.client_bind.event_message_reaction_remove.callback_add(reaction_hook)

        return self._event_reaction_remove

    @property
    def event_message_reaction_add2(self) -> EventDispenser[Tuple[StaticEmoji, LinkedMember]]:
        try:
            return self._message_data['event_reaction_add']
        except KeyError:
            new_dispenser = EventDispenser(self.client_bind.event_loop)
            self._message_data['event_reaction_add'] = new_dispenser
            return new_dispenser

    @property
    def event_message_reaction_remove2(self) -> EventDispenser[Tuple[StaticEmoji, LinkedMember]]:
        try:
            return self._message_data['event_reaction_remove']
        except KeyError:
            new_dispenser = EventDispenser(self.client_bind.event_loop)
            self._message_data['event_reaction_remove'] = new_dispenser
            return new_dispenser


class LinkedEmoji(AbstractEmoji):
    def __init__(self, parent_unit: GuildUnit, emoji_data: DataDict):
        self.parent_unit = parent_unit
        self._emoji_data = emoji_data

    @property
    def name(self) -> str:
        return self._emoji_data['name']

    @property
    def emoji_id(self) -> Optional[str]:
        return self._emoji_data['id']

    @property
    def is_animated(self) -> bool:
        return self._emoji_data['animated']
