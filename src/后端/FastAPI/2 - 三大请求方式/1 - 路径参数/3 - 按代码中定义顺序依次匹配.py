"""
路径参数按照代码中定义的顺序依次匹配

- FastAPI 的路由按照定义顺序依次匹配，请求一旦匹配成功就停止继续查找。
- 动态路径（如 /users/{user_id}）中的路径参数可以匹配任意符合类型约束的路径片段，因此 /users/me 也会被视为 user_id="me"。
- 越具体的路径放前面，越泛化的路径放后面。
- 因此，应当把固定路径放在前面，动态路径放在后面，避免固定路径被动态路径“抢先”匹配。
- 重复定义相同 HTTP 方法和相同路径（如两个 GET /users）时，第一个定义的路由会先匹配成功，后面的路由实际上不会被执行，因此这种写法没有实际意义，也应避免。

参考：https://fastapi.org.cn/tutorial/path-params/
"""

from fastapi import FastAPI

app = FastAPI()


# 注意以下定义的顺序
@app.get("/users/me")
async def get_me():
    return {"user_id": "the current user"}


@app.get("/users/admin")
async def get_admin():
    return {"user_id": "the admin"}


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}


def main():

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


"""
# 请求
curl -X GET http://127.0.0.1:8000/users/me \

# 返回
{
    "user_id": "the current user"
}
"""

"""
# 请求
curl -X GET http://127.0.0.1:8000/users/admin \

# 返回
{
    "user_id": "the admin"
}
"""

"""
# 请求
curl -X GET http://127.0.0.1:8000/users/tom \

# 返回
{
    "user_id": "tom"
}
"""
