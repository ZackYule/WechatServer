from enum import Enum


class MetaMessageType(Enum):
    TEXT = 1
    VOICE = 2
    IMAGE = 3
    FILE = 4
    VIDEO = 5
    SHARING = 6
    IMAGE_CREATE = 10
    ACCEPT_FRIEND = 19
    JOIN_GROUP = 20
    PATPAT = 21
    FUNCTION = 22
    EXIT_GROUP = 23

    def __str__(self):
        return self.name


class MetaMessage:

    def __init__(self, type: MetaMessageType = None, content=None, **kwargs):
        self.type = type
        self.content = content
        self.kwargs = kwargs

    def __getitem__(self, key):
        return getattr(self, key, self.kwargs.get(key))

    def __setitem__(self, key, value):
        if key in self.__dict__:
            setattr(self, key, value)
        else:
            self.kwargs[key] = value

    def __str__(self):
        return f"MetaMessage(type={self.type}, content={self.content}, kwargs={self.kwargs})"

    def get(self, key, default=None):
        return getattr(self, key, self.kwargs.get(key, default))
