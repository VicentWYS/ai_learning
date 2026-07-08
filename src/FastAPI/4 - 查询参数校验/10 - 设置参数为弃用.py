"""
参考：https://fastapi.org.cn/tutorial/query-params-str-validations/
"""

from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Annotated[
        list[str],
        Query(
            title="This is the title", description="This is the desc", deprecated=True
        ),
    ] = ["hello", "world"]
):
    query_items = {"q": q}
    return query_items


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl --location --request GET 'http://127.0.0.1:8000/items/?q=name_a&q=name_b'

# 返回
{
    "q": [
        "name_a",
        "name_b"
    ]
}
"""
