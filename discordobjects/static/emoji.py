class Emoji:

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str, name: str, animated: bool):
        self.emoji_id = id
        self.name = name
        self.animated = animated

    def is_unicode_emoji(self) -> bool:
        return self.emoji_id is None

    def __str__(self):
        if self.is_unicode_emoji():
            return self.name
        else:
            return f"<:{self.name}:{self.emoji_id}>"

    def __eq__(self, other):
        # TODO: coimpare unicode emojies to non unicode
        if self.is_unicode_emoji() and isinstance(other, str):
            return self.name == other
