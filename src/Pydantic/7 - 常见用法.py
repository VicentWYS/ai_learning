"""
几乎 80% 的 FastAPI 都是以下形式，
若请求体信息格式错误，则FastAPI不会进入函数，而是直接返回报错

请求
↓
Pydantic 校验
↓
成功？
↓
进入函数
"""

from fastapi import FastAPI
from pydantic import BaseModel, ValidationError

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


@app.post("/user")
def create_user(user: User):
    return {"message": "创建成功", "user": user}


def main():
    """使用 uvicorn 启动 FastAPI 开发服务器。"""
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 合法请求 → 200 OK，返回用户数据
curl -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "age": 25}'


# 返回结果：
{
    "message": "创建成功",
    "user": {
        "name": "张三",
        "age": 20
    }
}
"""
