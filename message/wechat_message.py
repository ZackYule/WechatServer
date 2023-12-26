import re
from message.chat_message import ChatMessage
from message.meta_message import MetaMessageType
from utils.tmp_dir import TmpDir
from utils.log_setup import log
from lib import itchat
from lib.itchat.content import TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING


class WechatMessage(ChatMessage):
    """
    WechatMessage 类用于表示从微信平台接收的聊天消息。该类继承自 ChatMessage。

    属性:
        message_id (str): 消息的唯一标识符，用于区分每个独立的消息。
        is_group (bool): 标识消息是否为群聊消息。True 表示群聊，False 表示私聊。
        create_time (datetime): 消息的创建时间，表示消息在微信平台上的发送时间。
        message_type (MetaMessageType): 消息的类型。可能的类型包括文本、图片、语音等，根据微信消息的性质而定。
        content (str): 消息的具体内容，如果消息类型为文本，则是文本内容；如果是媒体类型（如图片或语音），则是文件路径。
        sender_id (str): 发送者的唯一标识符。用于标识消息的发送方。
        sender_nickname (str): 发送者的昵称，用于在人性化的界面中显示发送者的名字。
        receiver_id (str): 接收者的唯一标识符，用于标识消息的接收方。
        receiver_nickname (str): 接收者的昵称，用于在人性化的界面中显示接收者的名字。
        other_user_id (str): 如果是私聊，则为对方的ID；如果是群聊，则为群的ID，用于区分聊天的上下文。
        other_user_nickname (str): 如果是私聊，则为对方的昵称；如果是群聊，则为群的昵称。
        actual_sender_id (str): 实际发送者的ID，仅在群聊中使用，表示消息的实际发送者。
        actual_sender_nickname (str): 实际发送者的昵称，仅在群聊中使用，表示消息的实际发送者昵称。
        self_display_name (str): 用户在群聊中的展示名称，如果设置了群昵称，则为群昵称。
        is_at (bool): 标识用户在消息中是否被@提及，仅在群聊中适用。
        prepare_fn (function): 准备函数，用于准备消息内容，例如下载媒体文件。
    """

    def __init__(self, itchat_msg, is_group=False):
        """
        初始化WechatMessage实例。

        :param itchat_msg: 原始的itchat消息对象。
        :param is_group: 指示消息是否来自群聊。
        """
        super().__init__(itchat_msg)
        self.message_id = itchat_msg["MsgId"]
        self.create_time = itchat_msg["CreateTime"]
        self.is_group = is_group
        self.sender_id = itchat_msg["FromUserName"]
        self.receiver_id = itchat_msg["ToUserName"]
        self._prepare_message()
        self._set_user_info()

    def _prepare_message(self):
        """
        准备和设置消息的内容和类型。
        """
        msg_type = self.raw_message["Type"]
        self.content, self.message_type, self.prepare_fn = None, None, None

        if msg_type in [TEXT, VOICE, PICTURE, ATTACHMENT]:
            self.content = TmpDir().path() + self.raw_message["FileName"]
            self.prepare_fn = lambda: self.raw_message.download(self.content)
            self.message_type = self._map_type_to_context(msg_type)
        elif msg_type == NOTE:
            self._process_note_message()
        elif msg_type == SHARING:
            self.message_type = MetaMessageType.SHARING
            self.content = self.raw_message.get("Url")
        else:
            raise NotImplementedError(
                f"Unsupported message type: Type:{msg_type}, MsgType:{self.raw_message['MsgType']}"
            )

    def _map_type_to_context(self, msg_type):
        """
        将微信消息类型映射到上下文类型。

        :param msg_type: 微信消息类型。
        :return: 映射后的上下文类型。
        """
        return {
            TEXT: MetaMessageType.TEXT,
            VOICE: MetaMessageType.VOICE,
            PICTURE: MetaMessageType.IMAGE,
            ATTACHMENT: MetaMessageType.FILE
        }.get(msg_type, None)

    def _process_note_message(self):
        """
        处理微信的注释消息类型。
        """
        content = self.raw_message["Content"]
        self.message_type = MetaMessageType.NOTE
        self.content = content

        if self.is_group:
            self._process_group_actions(content)
        elif "你已添加了" in content:
            self.message_type = MetaMessageType.ACCEPT_FRIEND
        elif "拍了拍我" in content:
            self.message_type = MetaMessageType.PATPAT
            self.actual_sender_nickname = self._extract_nickname(content)
        else:
            raise NotImplementedError(f"Unsupported note message: {content}")

    def _process_group_actions(self, content):
        """
        处理群组内的特殊行为，例如加入和退出群聊。

        :param content: 消息内容。
        """
        join_patterns = ["加入群聊", "加入了群聊"]
        if any(pattern in content for pattern in join_patterns):
            self.message_type = MetaMessageType.JOIN_GROUP
            self.actual_sender_nickname = self._extract_nickname(content)
        elif "移出了群聊" in content:
            self.message_type = MetaMessageType.EXIT_GROUP
            self.actual_sender_nickname = self._extract_nickname(content)

    @staticmethod
    def _extract_nickname(content):
        """
        从消息内容中提取昵称。

        :param content: 消息内容。
        :return: 提取的昵称。
        """
        return re.findall(r"\"(.*?)\"", content)[0]

    def _set_user_info(self):
        """
        设置与消息相关的用户信息。
        """
        user_id = itchat.instance.storageClass.userName
        nickname = itchat.instance.storageClass.nickName

        self._assign_user_nicknames(user_id, nickname)
        self._assign_other_user_info(user_id)

    def _assign_user_nicknames(self, user_id, nickname):
        """
        分配发送者和接收者的昵称。

        :param user_id: 当前用户的ID。
        :param nickname: 当前用户的昵称。
        """
        if self.sender_id == user_id:
            self.sender_nickname = nickname
        if self.receiver_id == user_id:
            self.receiver_nickname = nickname

    def _assign_other_user_info(self, user_id):
        """
        设置与消息相关的其他用户的信息。

        :param user_id: 当前用户的ID。
        """
        try:
            user_info = self.raw_message["User"]
            self.my_msg = self.raw_message["ToUserName"] == user_info["UserName"] and \
                          self.raw_message["ToUserName"] != self.raw_message["FromUserName"]
            self.other_user_id = user_info["UserName"]
            self.other_user_nickname = user_info["NickName"]
            self._assign_nicknames_for_other_user()
            if user_info.get("Self"):
                self.self_display_name = user_info["Self"].get("DisplayName")
        except KeyError as e:
            log.warn(f"[WX]get other_user_id failed: {e}")
            self.other_user_id = self.sender_id if self.sender_id != user_id else self.receiver_id

    def _assign_nicknames_for_other_user(self):
        """
        为其他用户分配昵称。
        """
        if self.other_user_id == self.sender_id:
            self.sender_nickname = self.other_user_nickname
        if self.other_user_id == self.receiver_id:
            self.receiver_nickname = self.other_user_nickname

        if self.is_group:
            self.is_at = self.raw_message["IsAt"]
            self.actual_sender_id = self.raw_message["ActualUserName"]
            if self.message_type not in [
                    MetaMessageType.JOIN_GROUP, MetaMessageType.PATPAT,
                    MetaMessageType.EXIT_GROUP
            ]:
                self.actual_sender_nickname = self.raw_message[
                    "ActualNickName"]
