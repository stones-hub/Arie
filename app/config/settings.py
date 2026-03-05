"""
集中配置：从环境变量读取，一处修改全局生效。
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，字段可从 .env 或环境变量读取。"""

    app_name: str = "Web API"
    debug: bool = False
    port: int = 8000  # 应用监听端口，默认 8000，可在 .env 中通过 APP_PORT 覆盖
    # 单库时只配 DATABASE_URL；多库时配 DATABASE_URL_USER + DATABASE_URL_DEPT（均为 MySQL 等）
    database_url: str = "sqlite:///./app.db"
    # 类型 str | None，未配置时默认 None；为 None 时 db/session 用 database_url 作为用户库连接。
    database_url_user: str | None = None
    # 类型 str | None，未配置时默认 None；为 None 时 db/session 用 database_url 作为部门库连接。
    database_url_dept: str | None = None
    # 日志文件路径与拆分策略（按大小滚动），可通过 LOG_FILE、LOG_MAX_BYTES、LOG_BACKUP_COUNT 配置
    log_file: str = "logs/app.log"
    log_max_bytes: int = 1_000_000  # 单个日志文件最大 1MB
    log_backup_count: int = 5       # 最多保留 5 个历史文件

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局单例，在 main.py 或依赖注入中使用
settings = Settings()
