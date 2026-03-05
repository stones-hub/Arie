"""
与请求解耦的日志等「事后执行」逻辑，适合放进 BackgroundTasks 中执行。
不阻塞响应，失败不影响主流程。

这里配置了一个按大小滚动的文件日志（RotatingFileHandler）：
- 日志文件路径、单文件大小、保留文件个数都从 Settings 里读取；
- 文件满了会自动切分并保留若干历史文件。
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config.settings import settings


def _get_logger() -> logging.Logger:
    """
    获取带文件滚动能力的 logger。

    - 日志文件位置由 settings.log_file 控制（默认 logs/app.log）。
    - 拆分策略由 settings.log_max_bytes、settings.log_backup_count 控制。
    """
    # 使用逻辑名称而不是看起来像文件名的字符串，避免混淆
    logger = logging.getLogger("app.audit")
    logger.setLevel(logging.INFO)

    # 避免重复添加 handler（如在热重载环境下）
    if not logger.handlers:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


logger = _get_logger()


def add_log(user_id: int, action: str, extra: str | None = None) -> None:
    """
    记录用户相关操作日志到文件（支持按大小拆分），设计为在 BackgroundTasks 中调用。

    - user_id: 相关用户 ID
    - action: 动作名称，如 \"get_user\"、\"create_user\"
    - extra: 额外信息（可选）
    """
    msg = f"user_id={user_id} action={action}"
    if extra:
        msg += f" extra={extra}"
    logger.info(msg)

