"""
可以声明多个请求体

在这种情况下，FastAPI 会注意到函数中有不止一个请求体参数（有两个参数是 Pydantic 模型）。
因此，它会将参数名作为请求体中的键（字段名），并期望请求体格式如下：

{
    "item_id": 123,
    "item": {
        "name": "Tom",
        "description": "This is a description",
        "price": 12.92,
        "tax": 20.33
    },
    "user": {
        "username": "Tom",
        "full_name": "Tom Cat"
    }
}
"""

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None  # 有默认值，可选
    price: float
    tax: float | None = None  # 有默认值，可选


class User(BaseModel):
    username: str
    full_name: str | None = None


app = FastAPI()


@app.post("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
