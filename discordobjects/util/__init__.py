from .enum_str import StrEnum
from .deprecated_dispencers import SingularEvent, QueueDispenser
from .event_dispenser import EventDispenser
from .coroutine_wrapper import wrap_if_coroutine
from .mapping_dict_cached import MappingDictCached


class SubclassedDict(dict):
    # HACK: allows to weak referencing the dictionary
    pass


__all__ = ['StrEnum', 'SingularEvent', 'QueueDispenser', 'EventDispenser', 'wrap_if_coroutine', 'SubclassedDict'
           , 'MappingDictCached']
