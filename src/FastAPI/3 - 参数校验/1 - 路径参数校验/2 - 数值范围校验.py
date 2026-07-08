"""
声明数值校验

- gt：greater than（大于）
- ge：greater than or equal（大于或等于）
- lt：less than（小于）
- le：less than or equal（小于或等于）
"""

from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1, le=8)],
    q: Annotated[str | None, Query(alias="item-query")],
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
