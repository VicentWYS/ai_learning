"""
约束路径参数使用预定义枚举值

这里参数中只能选择给定的三个枚举值，传入其他的值会报错。这一点在Swagger中会表现为下拉框。

文档：
Swagger: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

参考：https://fastapi.org.cn/tutorial/path-params/
"""

from fastapi import FastAPI
from enum import Enum


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


# 注意，这里请求参数只能是这三个模型名称之一，否则会报错

"""
# 请求
curl -X GET http://127.0.0.1:8000/models/resnet

# 返回
{
    "model_name": "resnet",
    "message": "Have some residuals"
}
"""
