import io
import threading
import qrcode as qrc
from PIL import Image


def qrCallback(uuid, status, qrcode):
    """
    微信登录过程中的二维码回调函数。
    
    :param uuid: 二维码的唯一标识符。
    :param status: 二维码的状态。
    :param qrcode: 二维码的图像数据。
    """
    if status == "0":
        try:
            # 使用 PIL 库显示二维码
            img = Image.open(io.BytesIO(qrcode))
            _thread = threading.Thread(target=img.show, args=("QRCode", ))
            _thread.setDaemon(True)
            _thread.start()
        except Exception as e:
            # 在这里可以处理异常，例如记录日志
            pass

        # 构建二维码的 URL
        url = f"https://login.weixin.qq.com/l/{uuid}"

        # 打印二维码的网址
        print("You can also scan QRCode in any website below:")
        print(f"https://api.pwmqr.com/qrcode/create/?url={url}")
        print(f"https://my.tv.sohu.com/user/a/wvideo/getQRCode.do?text={url}")
        print(
            f"https://api.qrserver.com/v1/create-qr-code/?size=400×400&data={url}"
        )
        print(f"https://api.isoyu.com/qr/?m=1&e=L&p=20&url={url}")

        # 使用 qrcode 库在控制台显示二维码
        qr = qrc.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)


# 示例调用
# qrCallback('your_uuid', '0', qrcode)
