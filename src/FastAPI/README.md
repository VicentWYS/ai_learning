## 特点
- FastAPI 官方教程：[FastAPI](https://fastapi.org.cn/learn/)
- FastAPI 完全基于 Pydantic
- 在测试时，最好结合postman使用，方便查看接口效果


## 自动生成交互式文档
FastAPI 的一大特色就是自动生成 API 文档。启动后可以访问：

- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

随着你添加更多接口和 Pydantic 模型，这两个页面会自动更新，无需手动维护文档。


## 常用命令

```bash
# 添加依赖
uv add fastapi
uv add "uvicorn[standard]"

# 启动开发服务器
uv run uvicorn main:app --reload

# 安装/同步依赖（例如克隆别人项目后）
uv sync
```

