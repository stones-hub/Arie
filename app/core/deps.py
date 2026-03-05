"""
公共依赖：多库时按需注入用户库 / 部门库 Session，请求结束自动 close。
"""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db import SessionUserLocal, SessionDeptLocal


def get_db_user() -> Generator[Session, None, None]:
    """用户库 Session（user 表所在库）。"""
    db = SessionUserLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_dept() -> Generator[Session, None, None]:
    """部门库 Session（部门表所在库）。"""
    db = SessionDeptLocal()
    try:
        yield db
    finally:
        db.close()
