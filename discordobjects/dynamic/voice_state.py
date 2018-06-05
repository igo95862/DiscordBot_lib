import asyncio
import typing

from .base_dynamic import BaseDynamic
from ..client import DiscordClientAsync
from ..util import StrEnum


class VoiceEvents(StrEnum):
    CONNECT = 'CONNECT'
    CHANGE_CHANNELS = 'CHANGE_CHANNELS'
    DISCONNECT = 'DISCONNECT'
    JOIN_CHANNEL = 'JOIN_CHANNEL'
    LEAVE_CHANNEL = 'LEAVE_CHANNEL'


class VoiceState:

    def __init__(self, user_id: str, session_id: str, deaf: bool, mute: bool,
                 self_deaf: bool, self_mute: bool, suppress: bool, self_video: bool,
                 channel_id: str, guild_id: str = None, member: dict = None):
        self.user_id = user_id
        self.session_id = session_id
        self.deaf = deaf
        self.mute = mute
        self.self_deaf = self_deaf
        self.self_mute = self_mute
        self.self_video = self_video
        self.suppress = suppress
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.member = member


class VoiceStateManager(BaseDynamic):

    def __init__(self, client_bind: DiscordClientAsync,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True
                 ):
        self.client_bind = client_bind
        self.voice_states: typing.Dict[str, VoiceState] = {}
        super().__init__(self.client_bind, VoiceEvents, event_loop, start_immediately)

    async def _auto_update(self):
        self.await_init.set_result(True)

        async for voice_state_dict in self.client_bind.event_gen_voice_state_update_gen():
            changed_user_id = voice_state_dict['user_id']
            try:
                old_voice_state = self.voice_states[changed_user_id]
                old_channel_id = old_voice_state.channel_id
                new_channel_id = voice_state_dict['channel_id']
                if new_channel_id is not None:
                    self._user_joined_chanel(changed_user_id, new_channel_id)

                if old_channel_id is not None:
                    self._user_left_channel(changed_user_id, old_channel_id)
                self.voice_states[changed_user_id].__init__(**voice_state_dict)

            except KeyError:
                new_voice_state = VoiceState(**voice_state_dict)
                self.voice_states[changed_user_id] = new_voice_state
                if new_voice_state.channel_id is not None:
                    self._user_joined_chanel(new_voice_state.user_id, new_voice_state.channel_id)

    def _user_joined_chanel(self, user_id: str, channel_id: str):
        coroutine = self.queue_dispenser.event_put(VoiceEvents.JOIN_CHANNEL, (user_id, channel_id))
        self.event_loop.create_task(coroutine)

    def _user_left_channel(self, user_id: str, channel_id: str):
        coroutine = self.queue_dispenser.event_put(VoiceEvents.LEAVE_CHANNEL, (user_id, channel_id))
        self.event_loop.create_task(coroutine)

    async def on_user_join_channel(self) -> typing.AsyncGenerator[typing.Tuple[str, str], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, VoiceEvents.JOIN_CHANNEL)
        while True:
            yield (await queue.get())[0]

    async def on_user_left_channel(self) -> typing.AsyncGenerator[typing.Tuple[str, str], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, VoiceEvents.LEAVE_CHANNEL)
        while True:
            yield (await queue.get())[0]
