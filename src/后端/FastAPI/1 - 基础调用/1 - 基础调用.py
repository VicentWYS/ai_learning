"""
一个最简单的FastAPI示例

参考：https://fastapi.org.cn/tutorial/first-steps/
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def main():

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()

"""
curl -X GET http://127.0.0.1:8000 \
"""
