import asyncio
import logging
import typing
import weakref


class QueueDispenser:

    def __init__(self, slot_names: typing.Tuple[str, ...]):
        self.queue_count = 0
        self.task = None
        self.is_running = False
        self.slots = {x: [] for x in slot_names}

    def queue_add_multiple_slots(self, queue: asyncio.Queue, slot_names: typing.Tuple[str, ...]):

        self.queue_count += 1
        new_weak_ref = weakref.ref(queue)
        for event_name in slot_names:
            self.slots[event_name].append(new_weak_ref)

        def queue_cleanup() -> None:
            for event_name in slot_names:
                self.slots[event_name].remove(new_weak_ref)
                self.queue_count -= 1

        weakref.finalize(queue, queue_cleanup)

    def queue_add_single_slot(self, queue: asyncio.Queue, slot_name: str):
        self.queue_add_multiple_slots(queue, (slot_name,))

    async def event_put(self, event_name: str, event_data: typing.Any):
        try:
            # print(f"Socket event with name {event_name} and data {event_data}")
            for queue_weakref in self.slots[event_name]:
                if queue_weakref() is not None:
                    queue_weakref().put_nowait((event_data, event_name))
        except KeyError:
            logging.warning(f"QueueDispenser. Tried to put event that does not have a slot: {event_name}")


class SingularEvent:

    def __init__(self, condition_function: typing.Callable[[dict, str], bool]):
        self.condition_function = condition_function
        self.future = asyncio.Future()

    def put_nowait(self, data_name_tuple: typing.Tuple[dict, str]):
        try:
            if self.condition_function(*data_name_tuple):
                self.future.set_result(data_name_tuple)
        except Exception as e:
            self.future.set_exception(e)
            logging.exception(f"Singular Event threw exception: {e}")

    def __await__(self) -> typing.Coroutine:
        return self.future.__await__()
