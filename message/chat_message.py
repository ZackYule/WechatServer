class ChatMessage:
    """
    聊天消息类，用于封装从不同平台（如 itchat 和 wechaty）接收的聊天消息。

    属性:
        - message_id: 消息ID
        - creation_time: 消息创建时间
        - message_type: 消息类型 (ContextType)
        - message_content: 消息内容（声音/图片的话为文件路径）
        - sender_id: 发送者ID
        - sender_nickname: 发送者昵称
        - receiver_id: 接收者ID
        - receiver_nickname: 接收者昵称
        - other_party_id: 对方ID（群聊为群ID）
        - other_party_nickname: 对方昵称
        - group_flag: 是否为群消息
        - mentioned: 是否被@提及
        - actual_sender_id: 实际发送者ID（群聊）
        - actual_sender_nickname: 实际发送者昵称
        - display_name: 自身展示名（群昵称）
        - mentioned_list: 被@的用户列表
        - prepare_function: 准备函数，用于消息内容准备
        - is_prepared: 消息是否已准备
        - raw_message: 原始消息对象
    """

    def __init__(self, raw_message):
        """
        初始化聊天消息对象。

        :param raw_message: 原始消息对象。
        """
        self.message_id = None
        self.creation_time = None

        self.message_type = None
        self.message_content = None

        self.sender_id = None
        self.sender_nickname = None
        self.receiver_id = None
        self.receiver_nickname = None
        self.other_party_id = None
        self.other_party_nickname = None
        self.group_flag = False
        self.mentioned = False
        self.actual_sender_id = None
        self.actual_sender_nickname = None
        self.display_name = None

        self.mentioned_list = None

        self.prepare_function = None
        self.is_prepared = False
        self.raw_message = raw_message

    def prepare(self):
        """
        准备消息内容。如果设置了 prepare_function 且消息未准备，则调用该函数。
        """
        if self.prepare_function and not self.is_prepared:
            self.is_prepared = True
            self.prepare_function()

    def __str__(self):
        """
        返回消息的字符串表示形式。
        """
        return (
            "ChatMessage: id={message_id}, creation_time={creation_time}, type={message_type}, "
            "content={message_content}, sender_id={sender_id}, sender_nickname={sender_nickname}, "
            "receiver_id={receiver_id}, receiver_nickname={receiver_nickname}, "
            "other_party_id={other_party_id}, other_party_nickname={other_party_nickname}, "
            "group_flag={group_flag}, mentioned={mentioned}, actual_sender_id={actual_sender_id}, "
            "actual_sender_nickname={actual_sender_nickname}, mentioned_list={mentioned_list}"
        ).format(**self.__dict__)


# itchat_message_data：

# MsgId: 消息的唯一标识符
# FromUserName: 发送者的ID
# ToUserName: 接收者的ID
# MsgType: 消息类型（例如，文本，图片）
# Content: 消息的实际内容
# Status: 消息的状态
# ImgStatus: 消息中图片的状态
# CreateTime: 消息创建的时间戳
# VoiceLength: 语音消息的长度（如果适用）
# PlayLength: 视频或音频播放长度（如果适用）
# FileName: 消息中附加文件的名称
# FileSize: 附加文件的大小
# MediaId: 附加媒体的媒体ID
# Url: 消息中包含的URL（如果有）
# AppMsgType: 应用程序消息的类型
# StatusNotifyCode: 状态通知的代码
# StatusNotifyUserName: 状态通知的用户名
# RecommendInfo: 推荐信息
# ForwardFlag: 消息是否被转发的标志
# AppInfo: 与消息相关的应用程序信息
# HasProductId: 消息相关的产品ID（如果适用）
# Ticket: 票据信息（如果适用）
# ImgHeight: 消息中图片的高度
# ImgWidth: 消息中图片的宽度
# SubMsgType: 消息的子类型
# NewMsgId: 新的消息标识符
# OriContent: 消息的原始内容
# EncryFileName: 加密的文件名（如果适用）
# User: 发送消息的用户信息
