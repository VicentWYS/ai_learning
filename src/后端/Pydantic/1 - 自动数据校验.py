"""
当函数的参数格式错误时，会自动转换为正确格式（如str -> int）；
若无法转换，会直接报错；
"""

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    """用户模型，演示 Pydantic 基本使用。"""

    name: str
    age: int


def create_user_right(name: str, age: int) -> User | None:
    try:
        user = User(name=name, age=age)
        print(user)
        return user
    except ValidationError:
        print(f"参数格式有误")
        return None


def main():
    # 正确调用：传入必填参数 name 和 age
    create_user_right(name="张三", age=25)
    
    # 自动数据校验：若输入格式异常，则自动转化为正确格式
    create_user_right(name="张三", age="25")

    # 若不能转换，则直接报错ValidationError
    create_user_right(name="李四", age="not_a_number")


if __name__ == "__main__":
    main()


"""
name='张三' age=25
name='张三' age=25
参数格式有误
"""