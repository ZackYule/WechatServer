import io
import os
import requests
from lib import itchat
from lib.itchat.content import TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING
from message.meta_message import MetaMessageType
from message.reply_message import Reply, ReplyType
from message_manager import MessageManager
from utils.log_setup import log
from message.universal_message import UniversalMessageWrapper
from utils.qr_callback import qrCallback


@itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING])
def handle_individual_message(msg):
    """
    处理单个微信消息。
    
    :param msg: 微信消息对象。
    :return: None
    """
    try:
        msg['IsGroup'] = False
        wrapped_msg = UniversalMessageWrapper(raw_message=msg,
                                              source='itchat',
                                              app='wechat')
        MessageManager().send_message(wrapped_msg)
    except NotImplementedError as e:
        log.debug(
            f"[WX] Skipped processing single message with ID {msg['MsgId']}: {e}"
        )


@itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING],
                     isGroupChat=True)
def handle_group_message(msg):
    """
    处理微信群聊消息。
    
    :param msg: 微信消息对象。
    :return: None
    """
    try:
        msg['IsGroup'] = True
        wrapped_msg = UniversalMessageWrapper(raw_message=msg,
                                              source='itchat',
                                              app='wechat')
        MessageManager().send_message(wrapped_msg)
    except NotImplementedError as e:
        log.debug(
            f"[WX] Skipped processing group message with ID {msg['MsgId']}: {e}"
        )


def send(reply: Reply, context: MetaMessageType):
    """
    根据回复类型发送消息。
    :param reply: Reply 对象，包含回复内容和类型。
    :param context: Context 对象，包含消息上下文信息。
    """
    receiver = context["receiver"]
    try:
        if reply['type'] in [
                ReplyType.TEXT.value, ReplyType.ERROR.value,
                ReplyType.INFO.value
        ]:
            itchat.send(reply['content'], toUserName=receiver)
            log.info(f"[WX] sendMsg={reply}, receiver={receiver}")

        elif reply['type'] == ReplyType.VOICE.value:
            itchat.send_file(reply['content'], toUserName=receiver)
            log.info(f"[WX] sendFile={reply['content']}, receiver={receiver}")

        elif reply['type'] == ReplyType.IMAGE_URL.value:  # 从网络下载图片
            img_url = reply['content']
            log.debug(f"[WX] start download image, img_url={img_url}")
            pic_res = requests.get(img_url, stream=True)
            image_storage = io.BytesIO()
            size = 0
            for block in pic_res.iter_content(1024):
                size += len(block)
                image_storage.write(block)
            log.info(
                f"[WX] download image success, size={size}, img_url={img_url}")
            image_storage.seek(0)
            itchat.send_image(image_storage, toUserName=receiver)
            log.info(f"[WX] sendImage url={img_url}, receiver={receiver}")

        elif reply['type'] == ReplyType.IMAGE.value:  # 从文件读取图片
            image_storage = reply['content']
            image_storage.seek(0)
            itchat.send_image(image_storage, toUserName=receiver)
            log.info(f"[WX] sendImage, receiver={receiver}")

        elif reply['type'] == ReplyType.FILE.value:  # 新增文件回复类型
            file_storage = reply['content']
            itchat.send_file(file_storage, toUserName=receiver)
            log.info(f"[WX] sendFile, receiver={receiver}")

        elif reply['type'] == ReplyType.VIDEO.value:  # 新增视频回复类型
            video_storage = reply['content']
            itchat.send_video(video_storage, toUserName=receiver)
            log.info(f"[WX] sendVideo, receiver={receiver}")

        elif reply['type'] == ReplyType.VIDEO_URL.value:  # 新增视频URL回复类型
            video_url = reply['content']
            log.debug(f"[WX] start download video, video_url={video_url}")
            video_res = requests.get(video_url, stream=True)
            video_storage = io.BytesIO()
            size = 0
            for block in video_res.iter_content(1024):
                size += len(block)
                video_storage.write(block)
            log.info(
                f"[WX] download video success, size={size}, video_url={video_url}"
            )
            video_storage.seek(0)
            itchat.send_video(video_storage, toUserName=receiver)
            log.info(f"[WX] sendVideo url={video_url}, receiver={receiver}")

    except Exception as e:
        log.error(f"Error sending message: {e}")


def process_message(message):
    log.debug(message['reply'])
    log.debug(message['context'])
    send(message['reply'], message['context'])


def main():
    # toDo: 之后写到配置项里
    hotReload = False
    status_path = "itchat.pkl"
    base_url = 'http://127.0.0.1:8000'

    # 启动消息管理
    manager = MessageManager(base_url, process_message)
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
