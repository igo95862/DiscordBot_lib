from typing import Iterator, _T_co, _KT, _VT_co

from collections.abc import Mapping
from typing import Generic, TypeVar, Type


TypeVarClass = TypeVar('TypeVarClass', object)

class MappingDictCached(Mapping, Generic[TypeVarClass]):
    def __init__(self, data_map: dict, class_type: Type[TypeVarClass]):
        self.data_map = data_map
        self.class_type = class_type

    def __getitem__(self, k: str) -> TypeVarClass:
        return self.class_type(self.data_map[k], k)

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[str]:
        pass