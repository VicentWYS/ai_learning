"""
路径参数可以是一个【路径】

文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

参考：https://fastapi.org.cn/tutorial/path-params/
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/files/a/b/tom.txt

# 返回
{
    "file_path": "a/b/tom.txt"
}
"""
