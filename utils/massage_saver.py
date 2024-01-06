import json
import os
from datetime import datetime


def save_message_to_json(msg, directory="json_messages"):
    """
    将消息保存为 JSON 文件。文件名包含时间戳和序号。

    :param msg: 要保存的消息，应为字典格式。
    :param directory: 存储 JSON 文件的目录，默认为 'json_messages'。
    """
    os.makedirs(directory, exist_ok=True)

    # 获取当前目录下最大的序号
    sequence_number = get_max_sequence_number(directory) + 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"message_{timestamp}_{sequence_number}.json"
    file_path = os.path.join(directory, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(msg, file, ensure_ascii=False, indent=4)


def get_max_sequence_number(directory):
    """
    获取指定目录下最大的文件序号。

    :param directory: 文件所在目录。
    :return: 最大序号。
    """
    max_seq = 0
    for filename in os.listdir(directory):
        parts = filename.split('_')
        if len(parts) == 3 and parts[0] == 'message':
            try:
                seq = int(parts[2].split('.')[0])
                max_seq = max(max_seq, seq)
            except ValueError:
                pass
    return max_seq
