"""
数据模型对象中可嵌套数据模型对象
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Car(BaseModel):
    name: str
    price: int


class User(BaseModel):
    """用户模型：FastAPI 会用此模型自动校验请求体字段。"""

    name: str
    age: int
    email: str
    car: Car


def main():
    user = User(
        name="Tom", age=12, email="123@qq.com", car={"name": "Ford", "price": 24000}
    )

    print(user.car.name)  # Ford
    print(user.car.price)  # 24000


if __name__ == "__main__":
    main()


"""
Ford
24000
"""
