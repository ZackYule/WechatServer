import re
from message.chat_message import ChatMessage
from message.meta_message import MetaMessageType
from utils.tmp_dir import TmpDir
from utils.log_setup import logger
from lib import itchat
from lib.itchat.content import TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING


class WechatMessage(ChatMessage):
    """
    WechatMessage 类表示从微信平台接收的聊天消息。该类的每个实例都包含以下属性：

    属性:
        message_id (str): 消息的唯一标识符。用于区分每个独立的消息。
        creation_time (datetime): 消息的创建时间。表示消息在微信平台上的发送时间。
        message_type (MetaMessageType): 消息的类型。可能的类型包括文本、图片、语音等，根据微信消息的性质而定。
        message_content (str): 消息的具体内容。如果消息类型为文本，则是文本内容；如果是媒体类型（如图片或语音），则是文件路径。
        sender_id (str): 发送者的唯一标识符。用于标识消息的发送方。
        sender_nickname (str): 发送者的昵称。用于在人性化的界面中显示发送者的名字。
        receiver_id (str): 接收者的唯一标识符。用于标识消息的接收方。
        receiver_nickname (str): 接收者的昵称。用于在人性化的界面中显示接收者的名字。
        other_party_id (str): 如果是私聊，则为对方的ID；如果是群聊，则为群的ID。用于区分聊天的上下文。
        other_party_nickname (str): 如果是私聊，则为对方的昵称；如果是群聊，则为群的昵称。
        group_flag (bool): 标识消息是否为群聊消息。True 表示群聊，False 表示私聊。
        mentioned (bool): 标识用户在消息中是否被@提及。仅在群聊中适用。
        actual_sender_id (str): 实际发送者的ID。在群聊中使用，表示消息的实际发送者。
        actual_sender_nickname (str): 实际发送者的昵称。在群聊中使用，表示消息的实际发送者昵称。
        display_name (str): 用户在群聊中的展示名称，如果用户设置了群昵称，则为群昵称。
        mentioned_list (list[str]): 被@提及的用户列表。包含所有在消息中被@的用户的ID。
        prepare_function (function): 准备函数，用于准备消息内容，例如下载媒体文件。
        is_prepared (bool): 标识消息内容是否已经通过 prepare_function 准备好。
        raw_message (object): 原始消息对象，包含微信平台提供的所有消息数据。
    """

    def __init__(self, itchat_msg, is_group=False):
        super().__init__(itchat_msg)
        self.msg_id = itchat_msg["MsgId"]
        self.create_time = itchat_msg["CreateTime"]
        self.is_group = is_group
        self.from_user_id = itchat_msg["FromUserName"]
        self.to_user_id = itchat_msg["ToUserName"]
        self._prepare_message(itchat_msg)
        self._set_user_info(itchat_msg)

    def _prepare_message(self, itchat_msg):
        """准备和设置消息的内容和类型。"""
        msg_type = itchat_msg["Type"]
        self.content, self.ctype, self._prepare_fn = None, None, None

        if msg_type in [TEXT, VOICE, PICTURE, ATTACHMENT]:
            self.content = TmpDir().path() + itchat_msg["FileName"]
            self._prepare_fn = lambda: itchat_msg.download(self.content)
            self.ctype = self._map_type_to_context(msg_type)
        elif msg_type == NOTE:
            self._process_note_message(itchat_msg)
        elif msg_type == SHARING:
            self.ctype = MetaMessageType.SHARING
            self.content = itchat_msg.get("Url")
        else:
            raise NotImplementedError(
                f"Unsupported message type: Type:{msg_type} MsgType:{itchat_msg['MsgType']}"
            )

    def _map_type_to_context(self, msg_type):
        """将微信消息类型映射到上下文类型。"""
        return {
            TEXT: MetaMessageType.TEXT,
            VOICE: MetaMessageType.VOICE,
            PICTURE: MetaMessageType.IMAGE,
            ATTACHMENT: MetaMessageType.FILE
        }.get(msg_type)

    def _process_note_message(self, itchat_msg):
        """处理微信的注释消息类型。"""
        content = itchat_msg["Content"]
        self.ctype = MetaMessageType.NOTE
        self.content = content

        if self.is_group:
            self._process_group_actions(content)
        elif "你已添加了" in content:
            self.ctype = MetaMessageType.ACCEPT_FRIEND
        elif "拍了拍我" in content:
            self.ctype = MetaMessageType.PATPAT
            self.actual_user_nickname = self._extract_nickname(content)
        else:
            raise NotImplementedError(f"Unsupported note message: {content}")

    def _process_group_actions(self, content):
        """处理群组内的特殊行为，例如加入和退出群聊。"""
        join_patterns = ["加入群聊", "加入了群聊"]
        if any(p in content for p in join_patterns):
            self.ctype = MetaMessageType.JOIN_GROUP
            self.actual_user_nickname = self._extract_nickname(content)
        elif "移出了群聊" in content:
            self.ctype = MetaMessageType.EXIT_GROUP
            self.actual_user_nickname = self._extract_nickname(content)

    @staticmethod
    def _extract_nickname(content):
        """从消息内容中提取昵称。"""
        return re.findall(r"\"(.*?)\"", content)[0]

    def _set_user_info(self, itchat_msg):
        """设置用户相关的信息。"""
        user_id = itchat.instance.storageClass.userName
        nickname = itchat.instance.storageClass.nickName

        self.from_user_nickname, self.to_user_nickname = None, None
        self._assign_user_nicknames(user_id, nickname, itchat_msg)
        self._assign_other_user_info(user_id, itchat_msg)

    def _assign_user_nicknames(self, user_id, nickname, itchat_msg):
        """分配发送者和接收者的昵称。"""
        if self.from_user_id == user_id:
            self.from_user_nickname = nickname
        if self.to_user_id == user_id:
            self.to_user_nickname = nickname

    def _assign_other_user_info(self, user_id, itchat_msg):
        """设置与消息相关的其他用户的信息。"""
        try:
            user_info = itchat_msg["User"]
            self.my_msg = itchat_msg["ToUserName"] == user_info[
                "UserName"] and itchat_msg["ToUserName"] != itchat_msg[
                    "FromUserName"]
            self.other_user_id = user_info["UserName"]
            self.other_user_nickname = user_info["NickName"]
            self._assign_nicknames_for_other_user(itchat_msg)
            if user_info.get("Self"):
                self.self_display_name = user_info["Self"].get("DisplayName")
        except KeyError as e:
            logger.warn(f"[WX]get other_user_id failed: {e}")
            self.other_user_id = self.from_user_id if self.from_user_id != user_id else self.to_user_id

    def _assign_nicknames_for_other_user(self, itchat_msg):
        """为其他用户分配昵称。"""
        if self.other_user_id == self.from_user_id:
            self.from_user_nickname = self.other_user_nickname
        if self.other_user_id == self.to_user_id:
            self.to_user_nickname = self.other_user_nickname

        if self.is_group:
            self.is_at = itchat_msg["IsAt"]
            self.actual_user_id = itchat_msg["ActualUserName"]
            if self.ctype not in [
                    MetaMessageType.JOIN_GROUP, MetaMessageType.PATPAT,
                    MetaMessageType.EXIT_GROUP
            ]:
                self.actual_user_nickname = itchat_msg["ActualNickName"]
