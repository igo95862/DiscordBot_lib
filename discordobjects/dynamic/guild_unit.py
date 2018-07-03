from ..client import DiscordClientAsync
from typing import Dict, NamedTuple, Tuple, List
from pprint import pprint
from asyncio import Future, AbstractEventLoop
from ..util import EventDispenser

'''
class UserData(NamedTuple):
    id: str
    username: str
    discriminator: str
    avatar: str
    bot: bool = None
    mfa_enabled: bool = None
    verified: bool = None
    email: str = None


class MemberData(NamedTuple):
    deaf: bool
    mute: bool
    joined_at: str
    nick: str = None
    roles_ids: Tuple = tuple()
'''


class GuildUnit:

    def __init__(self, client: DiscordClientAsync, guild_id: str, event_loop: AbstractEventLoop):
        self.client_bind = client
        self.guild_id = guild_id
        self.event_loop = event_loop

        self.members_data: Dict[str, Dict] = {}
        self.roles_data: Dict[str, Dict] = {}
        self.channels_data: Dict[str, Dict] = {}
        self.voice_states_data: Dict[str, Dict] = {}
        self.guild_data: Dict[str, Dict] = {}
        self.is_initialized: Future = Future(loop=event_loop)

        self.callback_guild_create = self.client_bind.event_guild_create.callback_add(self._on_guild_create)
        self.callback_guild_member_add = self.client_bind.event_guild_member_add(self._on_guild_member_add)

        # Events
        self.event_member_joined = EventDispenser(event_loop)
        self.event_member_update = EventDispenser(event_loop)
        self.event_member_removed = EventDispenser(event_loop)

    def _on_guild_member_add(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self.guild_id:
            user_id = event_data['user']['id']
            self.members_data[user_id] = event_data
            self.event_member_joined.put(LinkedMember(self, user_id))

    def _on_guild_member_update(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self.guild_id:
            user_id = event_data['user']['id']
            member_dict = self.members_data[user_id]
            member_dict['roles'] = event_data['roles']
            member_dict['user'] = event_data['user']
            member_dict['nick'] = event_data['nick']
            self.event_member_update.put(LinkedMember(self, user_id))

    def _on_guild_member_remove(self, event_data: Dict):
        guild_id = event_data['guild_id']
        if guild_id == self.guild_id:
            user_id = event_data['user']['id']
            self.members_data.pop(user_id)
            self.event_member_removed.put(LinkedMember(self, user_id))

    def _on_guild_create(self, event_data: Dict):
        if event_data['id'] == self.guild_id:
            roles_data = event_data.pop('roles')
            channels_data = event_data.pop('channels')
            members_data = event_data.pop('members')
            voice_states_data = event_data.pop('voice_states')
            self._populate_channels(roles_data)
            self._populate_channels(channels_data)
            self._populate_members(members_data)
            self._populate_voice_states(voice_states_data)
            self.guild_data = event_data
            self.is_initialized.set_result(True)

    def _populate_channels(self, channel_list: List[Dict]):
        self.channels_data = {x['id']: x for x in channel_list}

    def _populate_members(self, members_list: List[Dict]):
        self.members_data = {x['user']['id']: x for x in members_list}

    def _populate_roles(self, roles_list: List[Dict]):
        self.roles_data = {x['id']: x for x in roles_list}

    def _populate_voice_states(self, voice_states_list: List[Dict]):
        self.voice_states_data = {x['user_id']: x for x in voice_states_list}

    async def reload(self):
        pass

    def __await__(self):
        return self.is_initialized.__await__()


class BaseLinked:
    def __init__(self, parent_unit: GuildUnit):
        self.parent_unit = parent_unit


class LinkedMember(BaseLinked):
    def __init__(self, parent_unit: GuildUnit, member_id: str):
        self.member_id = member_id
        super().__init__(parent_unit)


class LinkedRole(BaseLinked):
    def __init__(self, parent_unit: GuildUnit, role_id: str):
        self.role_id = role_id
        super().__init__(parent_unit)


class LinkedChannel(BaseLinked):
    def __init__(self, parent_unit: GuildUnit, channel_id: str):
        self.channel_id = channel_id
        super().__init__(parent_unit)
