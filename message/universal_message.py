from pydantic import BaseModel


class UniversalMessageWrapper(BaseModel):
    raw_message: dict  # 假设 raw_message 是一个字典
    source: str  # 假设 source 是一个字符串
    app: str  # 假设 app 也是一个字符串

    # 如果有其他方法或验证逻辑，也可以在这里定义
