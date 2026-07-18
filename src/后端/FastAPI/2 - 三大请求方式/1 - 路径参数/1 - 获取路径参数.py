"""
获取路径参数

- 路径参数 item_id 的值将作为参数 item_id 传递给你的函数
- 如果你运行此示例并访问 http://127.0.0.1:8000/items/foo，你将看到如下响应：{"item_id":"foo"}
- 注意，这里没有对路径参数设置类型约束

参考：https://fastapi.org.cn/tutorial/path-params/
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/items/hello \

# 返回

{
    "item_id": "hello"
}
"""
