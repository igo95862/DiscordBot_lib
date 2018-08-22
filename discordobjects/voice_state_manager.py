from .client import DiscordClientAsync
from .util import EventDispenser
from typing import Tuple

class VoiceStateManager:

    def __init__(self, client: DiscordClientAsync):
        self.client = client
        self._voice_states_data = {}
        self.voice_update_callback_handle = client.event_voice_state_update.callback_add(self._on_voice_state_update)
        self.event_voice_channel_joined: EventDispenser[Tuple[str, str, str]] = EventDispenser(client.event_loop)
        
    def _on_voice_state_update(self, event_data: dict):
        user_id = event_data['user_id']
        try:
            old_channel_id = self._voice_states_data[user_id]['channel_id']
        except KeyError:
            old_channel_id = None

        try:
            new_channel_id =  event_data['channel_id']
        except KeyError:
            pass

        self._voice_states_data[user_id] = event_data