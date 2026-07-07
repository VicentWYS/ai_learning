"""
不只是简单的类型约束，还可以用 Annotated 对参数的长度等进行更加细致的约束

参考：https://fastapi.org.cn/tutorial/query-params-str-validations/
"""

from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=10)] = None):
    """
    限制参数q的最大字符数为10
    """
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

# 当参数q的字符数大于10时，会返回报错信息
"""
