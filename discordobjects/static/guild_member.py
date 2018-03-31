import typing

from .base_object import DiscordClient
from .guild_role import Role
from .user import User


class GuildMember(User):

    def __init__(self, client_bind: DiscordClient, user: dict, roles: typing.Tuple[str, ...],
                 joined_at: int, deaf: bool, mute: bool, nick: str = None,
                 parent_guild_id: str = None):
        super().__init__(client_bind, **user)

        self.nickname = nick
        self.roles_ids = roles
        self.joined_at = joined_at
        self.is_deaf = deaf
        self.is_mute = mute
        if not hasattr(self, 'parent_guild_id') or parent_guild_id is not None:
            self.parent_guild_id = parent_guild_id

    def kick(self) -> None:
        self.client_bind.guild_member_remove(self.parent_guild_id, self.snowflake)

    def add_role(self, role: Role):
        self.client_bind.guild_member_role_add(self.parent_guild_id, self.snowflake, role.snowflake)

    def remove_role(self, role: Role):
        self.client_bind.guild_member_role_remove(self.parent_guild_id, self.snowflake, role.snowflake)

    def set_roles(self, roles: typing.List[Role]):
        self.client_bind.guild_member_modify_roles(self.parent_guild_id, self.snowflake, [x.snowflake for x in roles])

    def set_roles_by_ids(self, roles_ids: typing.List[str]):
        self.client_bind.guild_member_modify_roles(self.parent_guild_id, self.snowflake, roles_ids)

    def roles_ids_iter(self) -> typing.Generator[str, None, None]:
        for i in self.roles_ids:
            yield i

    def update_from_dict(self, member_dict: dict):
        self.__init__(self.client_bind, **member_dict)

    def refresh(self) -> None:
        self.update_from_dict(**self.client_bind.guild_member_get(self.parent_guild_id, self.snowflake))

    @typing.overload
    def __contains__(self, item: Role) -> bool:
        ...

    def __contains__(self, item) -> bool:
        if isinstance(item, Role):
            return item.snowflake in self.roles_ids
        else:
            raise NotImplementedError
