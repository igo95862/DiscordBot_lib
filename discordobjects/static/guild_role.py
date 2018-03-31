from .base_object import DiscordClient, DiscordObject


class Role(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, name: str, color: int, hoist: bool, position: int,
                 permissions: int, managed: bool, mentionable: bool,
                 parent_guild_id: str = None):
        super().__init__(client_bind, id)
        self.role_name = name
        self.role_color = color
        self.display_separately = hoist
        self.position = position
        self.permissions = permissions
        self.managed = managed
        self.mentionable = mentionable
        self.parent_guild_id = parent_guild_id

    def has_name(self, other_name: str) -> bool:
        return self.role_name == other_name

    def get_role_name(self) -> str:
        return self.role_name

    def __repr__(self) -> str:
        return f"Role: {self.role_name}"
