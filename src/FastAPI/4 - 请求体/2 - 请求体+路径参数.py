"""
可以同时声明 路径参数+请求体。

FastAPI 将识别出与路径参数匹配的函数参数应该从路径中获取，而声明为 Pydantic 模型的函数参数应该从请求体中获取。

参考：https://fastapi.org.cn/tutorial/body/
"""

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str  # 必需
    description: str | None = None  # 有默认值，可选
    price: float  # 必需
    tax: float | None = None  # 有默认值，可选


app = FastAPI()


@app.post("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    获取请求体、请求参数的内容
    """

    return {"item_id": item_id, "item": item.model_dump()}


def main():

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X POST http://127.0.0.1:8000/items/23

# 请求体
{
    "name": "Tom",
    "description": "Tom is a caty in blue",
    "price": 122.33,
    "tax": 232.232  
}

# 返回
{
    "item_id": 23,
    "item": {
        "name": "Tom",
        "description": "Tom is a caty in blue",
        "price": 122.33,
        "tax": 232.232
    }
}
"""
