import logging
import typing

from ..client import DiscordClientAsync

extra_keys_dict: typing.Dict[str, typing.Set[typing.FrozenSet[str]]] = {}


class DiscordObject:
    """
    Basic class for all other discord objects
    """

    def __init__(self, client_bind: DiscordClientAsync = None, snowflake: str = None):
        self.client_bind = client_bind
        self.snowflake = snowflake

    def __eq__(self, other: 'DiscordObject') -> bool:
        return self.snowflake == other.snowflake

    @classmethod
    def kwargs_handler(cls, **kwargs):
        if not kwargs:
            return

        extra_keys = frozenset(kwargs.keys())

        try:
            post_warning = extra_keys not in extra_keys_dict[cls.__name__]
        except KeyError:
            extra_keys_dict[cls.__name__] = set()
            post_warning = True

        if post_warning:
            extra_keys_dict[cls.__name__].add(extra_keys)
            logging.warning(
                (f"DiscordObject Initialization warning. Object {cls.__name__}"
                 f" was attempted to initialize with the keys: "
                 f"{', '.join((str(k) for k in kwargs.keys()))}"))
