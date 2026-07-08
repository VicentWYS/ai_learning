"""
pydantic模型可以作为元素进行嵌套，也可以作为数组元素，总之可将其看做一般变量来组织
"""

from fastapi import FastAPI
from pydantic import BaseModel


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None  # 有默认值，可选
    price: float
    tax: float | None = None  # 有默认值，可选
    tags: set[str] = set()
    image: Image | None = None


app = FastAPI()


@app.post("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
