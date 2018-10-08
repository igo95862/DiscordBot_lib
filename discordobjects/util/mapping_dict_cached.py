from typing import Generic, TypeVar, Type, Dict
from typing import Iterator
from weakref import WeakValueDictionary

from collections.abc import Mapping

TypeVarClass = TypeVar('TypeVarClass', bound=object)


class MappingDictCached(Generic[TypeVarClass], Mapping):
    def __init__(self, data_container: object, data_map_name: str, class_type: Type[TypeVarClass]):
        self.data_map_name = data_map_name
        self.class_type = class_type
        self.data_container = data_container
        self.cache: Dict[str, TypeVarClass] = WeakValueDictionary()

    def __getitem__(self, k: str) -> TypeVarClass:
        try:
            return self.cache[k]
        except KeyError:
            new_instance = self.class_type(self.data_container, getattr(self.data_container, self.data_map_name)[k], k)
            self.cache[k] = new_instance
            return new_instance

    def __len__(self) -> int:
        return len(self.data_map)

    def __iter__(self) -> Iterator[str]:
        return iter(self.data_map)
