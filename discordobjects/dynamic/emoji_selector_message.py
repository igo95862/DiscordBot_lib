from ..static import Message
from ..client import DiscordClientAsync


class MessageEmojiSelector:

    def __init__(self, client_bind: DiscordClientAsync, channel_id: str, message_id: str, clear_new: bool = False):
        self.client_bind = client_bind
        self.channel_id = channel_id
        self.message_id = message_id
        self.message: Message = None
        self.clear_new = clear_new

    async def __aiter__(self):
        message = Message(
            self.client_bind, **(await self.client_bind.channel_message_get(self.channel_id, self.message_id)))
        async for emoji, user_id in message.on_emoji_created_async_gen():
            if self.clear_new:
                await message.clear_emoji_by_user(emoji, user_id)
            yield emoji, user_id
