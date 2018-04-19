from .base_object import DiscordObject
from ..client import DiscordClientAsync


class Attachment(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, filename: str, size: int, url: str, proxy_url: str,
                 height: int = None, width: int = None):
        super().__init__(client_bind, id)
        self.filename = filename
        self.file_size_bytes = size
        self.url = url
        self.proxy_url = proxy_url
        self.height = height
        self.width = width

    def is_image(self) -> bool:
        return self.height is not None
