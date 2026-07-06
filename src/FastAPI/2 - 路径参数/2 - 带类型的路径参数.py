"""
路径参数

参考：https://fastapi.org.cn/tutorial/path-params/

- 路径参数 item_id 的值将作为参数 item_id 传递给你的函数
- 在此例中，item_id 被声明为 int 类型，这将为你提供函数内部的编辑器支持，包括错误检查、补全等功能
- 若路径参数不是int，就会返回报错
- 注意，这里response的结果中，获取的值也是int类型，不是str

文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


def main():

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/items/1234 \

# 返回

{
    "item_id": 1234
}
"""

"""
# 请求
curl -X GET http://127.0.0.1:8000/items/hello \

# 返回

{
    "detail": [
        {
            "type": "int_parsing",
            "loc": [
                "path",
                "item_id"
            ],
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "hello"
        }
    ]
}
"""