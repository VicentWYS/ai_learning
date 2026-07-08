"""
查询参数中：
- 无默认值 -- 非必需项；
- 有默认值 -- 必需项；

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
