"""
可以用 Annotated 约束参数的最大、最小长度

参考：https://fastapi.org.cn/tutorial/query-params-str-validations/
"""

from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(min_length=2, max_length=10)] = None,
):
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

# 当参数q的字符数小于2，或者大于10时，会返回报错信息
"""
