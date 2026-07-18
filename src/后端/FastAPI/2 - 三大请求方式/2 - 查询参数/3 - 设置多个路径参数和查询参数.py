"""
可以同时声明多个路径参数和查询参数，FastAPI 会自动区分它们。

参考：https://fastapi.org.cn/tutorial/path-params/
文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{user_id}/items/{item_id}")
async def read_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}

    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )

    return item


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/users/1997/items/011220?q=tom&short=False

# 返回
{
    "item_id": "011220",
    "owner_id": 1997,
    "q": "tom",
    "description": "This is an amazing item that has a long description"
}
"""
