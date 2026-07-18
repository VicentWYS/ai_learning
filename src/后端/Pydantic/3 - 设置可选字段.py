"""
设置请求体中哪些为可选字段
"""

from fastapi import FastAPI
from pydantic import BaseModel, ValidationError

app = FastAPI()


class User(BaseModel):
    """用户模型：FastAPI 会用此模型自动校验请求体字段。"""

    name: str
    age: int
    email: str | None = None  # 如果请求体中不传这个字段，Pydantic 会自动将其设为 None


@app.post("/user")
def create_user(user: User):
    """创建用户：请求体自动校验为 User 模型后直接返回。"""
    return user


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

# 合法请求 → 200 OK，返回用户数据
curl -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","age":"12","email":"1234@qq.com"}'
"""
