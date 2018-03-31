class Emoji:

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str, name: str, animated: bool):
        self.emoji_id = id
        self.name = name
        self.animated = animated

    def is_unicode_emoji(self) -> bool:
        return self.emoji_id is None
