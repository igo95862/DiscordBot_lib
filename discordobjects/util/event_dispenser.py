from asyncio import Queue as AsyncioQueue, AbstractEventLoop, iscoroutinefunction
from collections import deque as Deque
from typing import (Deque as TypingDeque, TypeVar, Callable as TypingCallable, Coroutine as TypingCoroutine,
                    AsyncGenerator as TypingAsyncGenerator, Union as TypingUnion)
from weakref import ref as weak_ref

EventData = TypeVar('EventData')
CallbackType = TypingCallable[[EventData], None]
CoroutineType = TypingCoroutine[EventData, None, None]
WeakRefCallbackType = TypingCallable[[CallbackType], None]


class EventDispenser:

    def __init__(self, event_loop: AbstractEventLoop):
        self._callback_array: TypingDeque[WeakRefCallbackType] = Deque()
        self.event_loop = event_loop

    async def __aiter__(self) -> TypingAsyncGenerator[EventData, None]:
        new_queue = AsyncioQueue()

        def add_to_queue(event_data: EventData):
            new_queue.put_nowait(event_data)

        handle = self.callback_add(add_to_queue)
        while True:
            yield (await new_queue.get())

    def callback_add(self, new_callback: TypingUnion[CallbackType, CoroutineType]) -> 'CallbackHandle':
        if not iscoroutinefunction(new_callback):
            new_weak_ref = weak_ref(new_callback, self._clean_dead_ref)
            handle = CallbackHandle(self, new_callback)
        else:
            def coroutine_wraper(event_data: EventData):
                self.event_loop.create_task(new_callback(event_data))

            handle = CallbackHandle(self, coroutine_wraper, )
            new_weak_ref = weak_ref(coroutine_wraper, self._clean_dead_ref)

        self._callback_array.append(new_weak_ref)
        return handle

    def callback_remove(self, callback: CallbackType):
        self._callback_array = Deque((w for w in self._callback_array if w() != callback))

    def _clean_dead_ref(self, dead_ref: weak_ref):
        self._callback_array.remove(dead_ref)

    def put(self, event_data: EventData):
        for callback_weakref in self._callback_array:
            callback = callback_weakref()
            self.event_loop.call_soon(callback, event_data)


class CallbackHandle:

    def __init__(self, parent_dispenser: EventDispenser, callback_ref: CallbackType):
        self.parent_dispenser = parent_dispenser
        self.callback_ref = callback_ref

    def cancel(self):
        self.parent_dispenser.callback_remove(self.callback_ref)
