"""
User 业务逻辑：以类封装，面向对象风格，与 API 层 UserController 一致。

Session 按请求注入，不挂在实例上；方法内拿到的 user 是 User 实例（继承 Base），
可调用 user.to_dict()、repr(user) 等基类方法。
"""
import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """用户业务逻辑：增删改查，与 HTTP 解耦。"""

    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        """按 id 查询用户。"""
        return db.get(User, user_id)

    def get_user_by_email(self, db: Session, email: str) -> User | None:
        """按 email 查询用户。"""
        return db.execute(select(User).where(User.email == email)).scalars().first()

    def list_users( self, db: Session, *, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """分页列表。"""
        return db.execute(select(User).offset(skip).limit(limit)).scalars().all()

    def create_user(self, db: Session, payload: UserCreate) -> User:
        """创建用户。"""
        user = User(
            email=payload.email,
            name=payload.name,
            department_id=payload.department_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("created user: %s", user.to_dict())
        return user

    def update_user(self, db: Session, user: User, payload: UserUpdate) -> User:
        """更新用户，仅更新 payload 中非 None 的字段。"""
        if payload.email is not None:
            user.email = payload.email
        if payload.name is not None:
            user.name = payload.name
        if payload.department_id is not None:
            user.department_id = payload.department_id
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user: User) -> None:
        """删除用户。"""
        db.delete(user)
        db.commit()

# 模块级单例，供 API 层注入使用；Session 仍由各请求的 Depends(get_db_user) 提供
user_service = UserService()
