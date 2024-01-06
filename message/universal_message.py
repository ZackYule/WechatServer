from pydantic import BaseModel, Field
from typing import Optional


class UniversalMessageWrapper(BaseModel):
    raw_message: dict
    source: str
    app: str
    receiver_id: str
    sender_id: Optional[str] = None
    group_flag: Optional[int] = Field(
        None,
        description="0 for private chat, 1 for group chat, None if uncertain")

    class Config:
        # 使用Config类来提供模型的配置
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "raw_message": {
                    "type": "text",
                    "content": "Hello!"
                },
                "source": "wechat",
                "app": "my_chat_app",
                "receiver_id": "receiver123",
                "sender_id": "sender456",
                "group_flag": -1
            }
        }


def main():
    example_message = UniversalMessageWrapper(
        raw_message={
            "type": "text",
            "content": "Hello, world!"
        },
        source="example_source",
        app="example_app",
        receiver_id="example_receiver",
        sender_id="example_sender",
        # group_flag 可以省略
    )

    print(example_message)


if __name__ == '__main__':
    main()
# 示例使用
