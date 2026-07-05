"""
可限制请求体中参数的取值范围
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class User(BaseModel):
    """用户模型：FastAPI 会用此模型自动校验请求体字段。"""

    name: str = Field(min_length=2, max_length=20)  # 2~20个字符数（含）
    age: int = Field(ge=0, le=120)  # 0~120以内（含）
    email: str | None = None


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
  -d '{"name":"张三","age":"12","email":"1234@qq.com"}'

# 非法请求 → age属性值超出了120
curl -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","age":"200","email":"1234@qq.com"}'
"""
