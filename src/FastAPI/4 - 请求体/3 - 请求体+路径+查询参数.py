"""
可以同时声明 请求体+路径+查询参数

FastAPI 将识别它们中的每一个，并从正确的地方获取数据。

- 如果参数也在路径中声明，它将被用作路径参数。
- 如果参数是标量类型（如 int、float、str、bool 等），它将被解释为查询参数。
- 如果参数被声明为 Pydantic 模型类型，它将被解释为请求体。


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
async def update_item(item_id: int, item: Item, q: str | None = None):
    """
    获取请求体、请求参数的内容
    """
    result = {"item_id": item_id, "item": item.model_dump()}

    if q:
        result.update({"q": q})

    return result


def main():

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X POST http://127.0.0.1:8000/items/23?q=tom

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
    },
    "q": "tom"
}
"""
