from enum import Enum


class MetaMessageType(Enum):
    # 枚举类，定义不同类型的上下文
    TEXT = 1  # 文本消息
    VOICE = 2  # 音频消息
    IMAGE = 3  # 图片消息
    FILE = 4  # 文件信息
    VIDEO = 5  # 视频信息
    SHARING = 6  # 分享信息

    IMAGE_CREATE = 10  # 创建图片命令
    ACCEPT_FRIEND = 19  # 同意好友请求
    JOIN_GROUP = 20  # 加入群聊
    PATPAT = 21  # 拍了拍
    FUNCTION = 22  # 函数调用
    EXIT_GROUP = 23  # 退出群聊

    def __str__(self):
        # 返回枚举成员的名称
        return self.name


class MetaMessage:
    # MetaMessage类，用于封装与MetaMessageType相关的信息
    def __init__(self, type: MetaMessageType = None, content=None, **kwargs):
        self.type = type
        self.content = content
        self.kwargs = kwargs

    def __contains__(self, key):
        # 支持使用'in'检查键是否存在
        if key in ['type', 'content']:
            return getattr(self, key) is not None
        return key in self.kwargs

    def __getitem__(self, key):
        # 支持使用索引访问属性
        if key in ['type', 'content']:
            return getattr(self, key)
        return self.kwargs.get(key)

    def get(self, key, default=None):
        # 获取指定键的值，如果不存在则返回默认值
        return self.__getitem__(key) if key in self else default

    def __setitem__(self, key, value):
        # 支持使用索引设置属性
        if key in ['type', 'content']:
            setattr(self, key, value)
        else:
            self.kwargs[key] = value

    def __delitem__(self, key):
        # 支持使用del删除属性
        if key in ['type', 'content']:
            setattr(self, key, None)
        else:
            del self.kwargs[key]

    def __str__(self):
        # 返回对象的字符串表示
        return f"MetaMessage(type={self.type}, content={self.content}, kwargs={self.kwargs})"
