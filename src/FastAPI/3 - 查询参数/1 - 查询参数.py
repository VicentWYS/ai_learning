"""
当声明不属于路径参数的其他函数参数时，它们会自动被解释为“查询”参数。
对应的url为类似：http://127.0.0.1:8000/items/?skip=10&limit=122

这里对两个查询参数分别设置了默认值：
- skip: 值为 0
- limit: 值为 10

参考：https://fastapi.org.cn/tutorial/path-params/
文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/items/?skip=10&limit=122

# 返回
{
    "skip": 10,
    "limit": 122
}
"""
