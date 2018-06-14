from enum import Enum
from typing import overload as typing_overload


class StrEnum(str, Enum):
    """
    Enum where members are also (and must be) strings
    Based on IntEnum implementation in main library
    """

    # HACK: code analyser does not understand that enums do not return the values directly but instead return subclass
    @typing_overload
    def __iter__(self) -> Enum:
        ...

    def __iter__(self):
        return super().__iter__()
