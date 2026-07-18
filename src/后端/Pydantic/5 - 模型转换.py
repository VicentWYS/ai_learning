"""
可将模型类对象转化为dict或JSON

- model_dump()
- model_dump_json()
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class User(BaseModel):
    """用户模型：FastAPI 会用此模型自动校验请求体字段。"""

    name: str
    age: int
    email: str


def main():
    user = User(name="Tom", age=12, email="123@qq.com")

    print(user.model_dump())  # 返回一个 dict
    print(user.model_dump_json())  # 返回一个 JSON


if __name__ == "__main__":
    main()


"""
{'name': 'Tom', 'age': 12, 'email': '123@qq.com'}
{"name":"Tom","age":12,"email":"123@qq.com"}
"""
