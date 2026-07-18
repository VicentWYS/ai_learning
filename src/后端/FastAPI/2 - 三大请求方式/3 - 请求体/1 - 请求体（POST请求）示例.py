"""
请求体是客户端发送给 API 的数据（常用POST实现）。响应体是 API 发送给客户端的数据。
要声明请求体，你可以使用 Pydantic 模型，充分利用其强大的功能和优势。

通过这种 Python 类型声明，FastAPI 就会：
- 将请求体读取为 JSON。
- 转换相应的类型（如果需要）。
- 验证数据：如果数据无效，它将返回一个清晰明了的错误，精确指出错误数据的具体位置和原因。
- 在参数 item 中为你提供接收到的数据：由于在函数中将其声明为 Item 类型，你还将获得所有属性及其类型的编辑器支持（补全等）。
- 为你的模型生成 JSON Schema 定义，如果对你的项目有意义，你也可以在其他任何地方使用它们。
- 这些架构将成为生成的 OpenAPI 架构的一部分，并被自动文档 UI 所使用。

模型的 JSON Schema 将成为 OpenAPI 生成的架构的一部分，并显示在交互式 API 文档中
"""

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None  # 有默认值，可选
    price: float
    tax: float | None = None  # 有默认值，可选


app = FastAPI()


@app.post("/items/")
async def create_item(item: Item):
    """
    获取请求体的内容
    """
    item_dict = item.model_dump()  # pydantic中的用法，将 BaseModel 对象转换为一个 dict
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X POST http://127.0.0.1:8000/items

# 请求体
{
    "name": "Tom",
    "description": "Tom is a caty in blue",
    "price": 122.33,
    "tax": 232.232  
}

# 返回
{
    "name": "Tom",
    "description": "Tom is a caty in blue",
    "price": 122.33,
    "tax": 232.232,
    "price_with_tax": 354.562
}
"""
