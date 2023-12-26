from enum import Enum


class ReplyType(Enum):
    """
    ReplyType 枚举，定义了不同类型的回复内容。

    枚举值:
    - TEXT: 文本回复
    - VOICE: 音频文件
    - IMAGE: 图片文件
    - IMAGE_URL: 图片URL
    - VIDEO_URL: 视频URL
    - FILE: 文件
    - CARD: 微信名片，仅支持ntchat
    - InviteRoom: 邀请加入群聊
    - INFO: 信息
    - ERROR: 错误
    - TEXT_: 强制文本
    - VIDEO: 视频
    - MINIAPP: 小程序
    """
    TEXT = 1
    VOICE = 2
    IMAGE = 3
    IMAGE_URL = 4
    VIDEO_URL = 5
    FILE = 6
    CARD = 7
    InviteRoom = 8
    INFO = 9
    ERROR = 10
    TEXT_ = 11
    VIDEO = 12
    MINIAPP = 13

    def __str__(self):
        # 返回枚举成员的名称
        return self.name


class Reply:
    """
    Reply 类用于创建不同类型的回复。

    属性:
    - type (ReplyType): 回复的类型。
    - content: 回复的内容，可以是文本、URL或文件路径等。
    - receiver: 回复的接收者，默认为 None。
    """

    def __init__(self, type: ReplyType = None, content=None, receiver=None):
        self.type = type
        self.content = content
        self.receiver = receiver

    def __str__(self):
        return f"Reply(type={self.type}, content={self.content}, receiver={self.receiver})"
