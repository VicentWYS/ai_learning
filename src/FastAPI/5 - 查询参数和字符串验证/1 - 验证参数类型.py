"""
可以对请求参数进行约束，使其符合指定格式

参考：https://fastapi.org.cn/tutorial/query-params-str-validations/
"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/")
async def read_items(q: str | None = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/items/?q=tom

# 返回
{
    "items": [
        {
            "item_id": "Foo"
        },
        {
            "item_id": "Bar"
        }
    ],
    "q": "tom"
}
"""