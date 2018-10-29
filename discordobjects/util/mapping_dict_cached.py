from typing import Generic, TypeVar, Dict, Callable
from typing import Iterator
from weakref import WeakValueDictionary

from collections.abc import Mapping

TypeVarClass = TypeVar('TypeVarClass', bound=object)


class MappingDictCached(Generic[TypeVarClass], Mapping):

    # def __init__(self, data_container: object, data_map_name: str, class_type: Type[TypeVarClass]):
    def __init__(self,  init_func: Callable[[str], TypeVarClass], len_func: Callable[..., int],
                 iter_func: Callable[..., Iterator[str]]):
        self._init_func = init_func
        self._len_func = len_func
        self._iter_func = iter_func
        self._cache: Dict[str, TypeVarClass] = WeakValueDictionary()

    def __getitem__(self, k: str) -> TypeVarClass:
        try:
            return self._cache[k]
        except KeyError:
            new_instance = self._init_func(k)
            self._cache[k] = new_instance
            return new_instance

    def __len__(self) -> int:
        return self._len_func()

    def __iter__(self) -> Iterator[str]:
        return self._iter_func()
