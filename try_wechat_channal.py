import io
import os
from typing import Any, Dict
import requests
from lib import itchat
from lib.itchat.content import TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING
from message.meta_message import MetaMessageType
from message.reply_message import Reply, ReplyType
from message_manager import MessageManager
from utils.log_setup import log
from message.universal_message import UniversalMessageWrapper
from utils.qr_callback import qrCallback


def process_message(msg: Dict[str, Any], group_flag: int):
    """
    处理微信消息，并封装成 UniversalMessageWrapper。

    :param msg: 微信消息对象。
    :param group_flag: 群聊标志，0 表示私聊，1 表示群聊。
    :return: None
    """
    try:
        # 获取发送者和接收者的ID
        sender_id = msg["FromUserName"]
        receiver_id = msg["ToUserName"]

        # 封装消息
        wrapped_msg = UniversalMessageWrapper(raw_message=msg,
                                              source='itchat',
                                              app='wechat',
                                              receiver_id=receiver_id,
                                              sender_id=sender_id,
                                              group_flag=group_flag)

        # 发送消息
        MessageManager().send_message(wrapped_msg)
    except NotImplementedError as e:
        log.debug(
            f"[WX] Skipped processing message with ID {msg['MsgId']}: {e}")


# 注册处理个人消息的函数
@itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING])
def handle_individual_message(msg: Dict[str, Any]):
    """
    处理单个微信消息。
    
    :param msg: 微信消息对象。
    :return: None
    """
    log.info('收到私聊消息🚀🚀🚀🚀🚀🚀')
    msg['IsGroup'] = False
    process_message(msg, group_flag=0)


# 注册处理群聊消息的函数
@itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING],
                     isGroupChat=True)
def handle_group_message(msg: Dict[str, Any]):
    """
    处理微信群聊消息。
    
    :param msg: 微信消息对象。
    :return: None
    """
    log.info('收到群聊消息🚀🚀🚀🚀🚀🚀')
    msg['IsGroup'] = True
    process_message(msg, group_flag=1)


def send_message(message: UniversalMessageWrapper):
    """
    根据回复类型发送消息。

    :param reply: 包含回复内容和类型的字典。
    :param context: 包含消息上下文信息的字典。
    """
    receiver = message["receiver_id"]
    reply = message['raw_message']
    try:
        if reply['type'] in [
                ReplyType.TEXT.value, ReplyType.ERROR.value,
                ReplyType.INFO.value
        ]:
            # 发送文本消息
            itchat.send(reply['content'], toUserName=receiver)
            log.info(f"[WX] sendMsg={reply}, receiver={receiver}")

        elif reply['type'] == ReplyType.VOICE.value:
            # 发送语音文件
            itchat.send_file(reply['content'], toUserName=receiver)
            log.info(f"[WX] sendFile={reply['content']}, receiver={receiver}")

        elif reply['type'] in [
                ReplyType.IMAGE_URL.value, ReplyType.VIDEO_URL.value
        ]:
            # 从URL下载图片或视频并发送
            send_media_from_url(reply, receiver)

        elif reply['type'] in [
                ReplyType.IMAGE.value, ReplyType.FILE.value,
                ReplyType.VIDEO.value
        ]:
            # 直接发送文件（图片、普通文件或视频）
            itchat.send_file(reply['content'], toUserName=receiver)
            log.info(f"[WX] sendFile, receiver={receiver}")

    except Exception as e:
        log.error(f"Error sending message: {e}")


def send_media_from_url(reply, receiver):
    """
    从URL下载媒体文件（图片或视频）并发送。

    :param reply: 包含媒体URL的回复字典。
    :param receiver: 消息接收者。
    """
    media_url = reply['content']
    log.debug(f"[WX] start download media, media_url={media_url}")
    media_res = requests.get(media_url, stream=True)
    media_storage = io.BytesIO()

    for block in media_res.iter_content(1024):
        media_storage.write(block)

    media_size = media_storage.tell()
    log.info(
        f"[WX] download media success, size={media_size}, media_url={media_url}"
    )
    media_storage.seek(0)

    if reply['type'] == ReplyType.IMAGE_URL.value:
        itchat.send_image(media_storage, toUserName=receiver)
        log.info(f"[WX] sendImage url={media_url}, receiver={receiver}")
    else:
        itchat.send_video(media_storage, toUserName=receiver)
        log.info(f"[WX] sendVideo url={media_url}, receiver={receiver}")


def main():
    # toDo: 之后写到配置项里
    hotReload = False
    status_path = "itchat.pkl"
    base_url = 'http://127.0.0.1:8000'

    # 启动消息管理
    manager = MessageManager(base_url, send_message)
    manager.start()

    # 修改断线超时时间
    itchat.instance.receivingRetryCount = 600

    # 登陆
    itchat.auto_login(
        enableCmdQR=2,
        hotReload=hotReload,
        statusStorageDir=status_path,
        qrCallback=qrCallback,
    )

    # 用户登陆提示
    user_id = itchat.instance.storageClass.userName
    name = itchat.instance.storageClass.nickName
    log.info("Wechat login success, user_id: {}, nickname: {}".format(
        user_id, name))

    # start message listener
    itchat.run()


if __name__ == '__main__':
    main()
