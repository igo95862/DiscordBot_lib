from ..client import DiscordClientAsync


class DiscordObject:
    """
    Basic class for all other discord objects
    """

    def __init__(self, client_bind: DiscordClientAsync = None, snowflake: str = None):
        self.client_bind = client_bind
        self.snowflake = snowflake

    def __eq__(self, other: 'DiscordObject') -> bool:
        return self.snowflake == other.snowflake
