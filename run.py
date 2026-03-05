"""
应用启动脚本：从配置读取端口，启动 FastAPI 应用。

用法：
    python run.py
或显式指定 host/port：
    APP_PORT=9000 python run.py
"""
import uvicorn

from app.config.settings import settings


def main() -> None:
    """根据配置启动应用。"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()

