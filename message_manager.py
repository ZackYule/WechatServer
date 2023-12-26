import asyncio
import json
import threading
import queue
import requests
import time
from message.universal_message import UniversalMessageWrapper

from utils.singleton import singleton
from utils.log_setup import log


@singleton
class MessageManager:

    def __init__(self, base_url, process_fn):
        self.base_url = base_url
        self.process_fn = process_fn
        self.recv_queue = queue.Queue()
        self.send_queue = queue.Queue()
        self.message_post_path = '/send'
        self.sse_path = '/events'
        self.max_retry = 5
        self.retry_delay = 300  # 5 minutes

    def start(self):
        threading.Thread(target=self.listen_sse).start()
        threading.Thread(target=self.process_messages).start()
        threading.Thread(target=self.process_send_queue).start()

    def send_message(self, message):
        self._add_message_to_send_queue(message)

    def _add_message_to_send_queue(self, message):
        self.send_queue.put({
            'message': message,
            'timestamp': time.time(),
            'retry_count': 0
        })

    async def async_send_message(self, message_data):
        message_json = json.dumps(message_data['message'].model_dump())
        log.debug(message_json)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.base_url + self.message_post_path,
                                 data=message_json,
                                 headers=headers)
        log.debug(response)
        if response.status_code == 200:
            # 如果请求成功，则将响应的内容放入接收队列
            res = response.json()
            data = res.get('data', None)
            if data is not None:
                self.recv_queue.put(data)

            message = res.get('message', None)
            if message is not None:
                log.info(message)
        else:
            # 如果请求失败，则重新加入发送队列末尾等待再次发送
            self.send_queue.put(message_data)

    def listen_sse(self):
        while True:
            try:
                log.debug('listening...')
                headers = {'Accept': 'text/event-stream'}
                with requests.get(self.base_url + self.sse_path,
                                  stream=True,
                                  headers=headers,
                                  timeout=80) as r:
                    for chunk in r.iter_content(chunk_size=102400):
                        log.debug(chunk)
                        # 首先，将字节数据解码为字符串
                        string_data = chunk.decode('utf-8')

                        # 然后，使用json.loads将字符串转换为字典
                        json_data = json.loads(string_data)
                        data = json_data.get('data', None)
                        log.debug(data)
                        if data is not None:
                            self.recv_queue.put(data)
            except requests.exceptions.RequestException as e:
                # 处理网络请求相关的异常
                log.error(f"Network error occurred: {e}")
            except Exception as e:
                # 处理其他可能的异常
                log.error(f"An error occurred: {e}")

    def process_send_queue(self):
        while True:
            if not self.send_queue.empty():
                message_data = self.send_queue.get()
                current_time = time.time()
                if current_time - message_data['timestamp'] > self.retry_delay:
                    message_data['retry_count'] += 1
                    message_data['timestamp'] = current_time
                asyncio.run(self.async_send_message(message_data))

    def process_messages(self):
        while True:
            if not self.recv_queue.empty():
                message = self.recv_queue.get()
                self.process_fn(message)


# 使用示例
def fn(message):
    print("处理消息:", message)


def process_message(message):
    log.info(message['reply'])
    log.info(message['context'])


def main():
    base_url = 'http://127.0.0.1:8000'
    manager = MessageManager(base_url, process_message)
    manager.start()

    file_path = "itchat_message_data_20231224_160954.json"  # 确保这是正确的文件路径
    with open(file_path, 'r', encoding='utf-8') as file:
        message_data = json.load(file)

    wrapped_msg = UniversalMessageWrapper(raw_message=message_data,
                                          source='itchat',
                                          app='wechat')
    MessageManager().send_message(wrapped_msg)
    # manager.send_message({'data': 'Hello World'})


if __name__ == '__main__':
    main()
