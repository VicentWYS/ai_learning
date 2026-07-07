"""
有些情况下，你需要进行一些无法通过上述参数完成的自定义验证。
在这些情况下，你可以使用一个自定义验证器函数，它在常规验证之后（例如在验证值确实是 str 之后）执行。
你可以通过在 Annotated 中使用 Pydantic 的 AfterValidator 来实现。

参考：https://fastapi.org.cn/tutorial/query-params-str-validations/
"""

import random
from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import AfterValidator

app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def chceck_valid_id(id: str):
    """
    检查参数是否为指定格式开头
    """
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/items/")
async def read_items(id: Annotated[str | None, AfterValidator(chceck_valid_id)] = None):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))  # 从data中获取对应的值

    return {"id": id, "item": item}


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl --location --request GET 'http://127.0.0.1:8000/items/?id=isbn-9781529046137'

# 返回
{
    "id": "isbn-9781529046137",
    "item": "The Hitchhiker's Guide to the Galaxy"
}
"""
