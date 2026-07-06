"""
查询参数中：
- 给出默认值的：非必需项；
- 未给出默认值的：必需项；

参考：https://fastapi.org.cn/tutorial/path-params/
文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}

    return item


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/items/tom?needy=yeah

# 返回
{
    "item_id": "tom",
    "needy": "yeah"
}
"""
