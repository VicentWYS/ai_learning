"""
当声明不属于路径参数的其他函数参数时，它们会自动被解释为“查询”参数。
对应的url为类似：http://127.0.0.1:8000/items/?skip=10&limit=122

这里对两个查询参数分别设置了默认值：
- skip: 值为 0
- limit: 值为 10

可以通过将默认值设为 None 来声明可选查询参数。
在以下情况中，函数参数 q 是可选的，并且默认值为 None。

- item_id: 路径参数
- q: 查询参数

参考：https://fastapi.org.cn/tutorial/path-params/
文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/items/12?q=10

# 返回
{
    "item_id": "12",
    "q": "10"
}
"""
