"""
用户相关：一张表对应一个 ORM 类，其余是 API 用 Schema（不落库）。

- ORM 模型（对应数据库表）：仅 User，与表 user 一一对应。
- Pydantic Schema（不对应表）：UserBase / UserCreate / UserUpdate / UserResponse / UserWithDepartmentResponse，
  用于请求体校验、响应体结构，不参与建表。
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.department import DepartmentResponse

from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base as OrmBase


# ---------- 仅此一个类对应数据库表 user ----------


class User(OrmBase):
    """用户表。"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 关联部门（部门表在另一库，仅存 id，不做数据库级 FK）
    department_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


# ---------- 以下均为 Pydantic Schema，不对应表，只用于 API 入参/出参 ----------


class UserBase(BaseModel):
    email: EmailStr
    name: str
    department_id: Optional[int] = None


class UserCreate(UserBase):
    """创建用户请求体。"""
    pass


class UserUpdate(BaseModel):
    """更新用户请求体，字段可选。"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    department_id: Optional[int] = None


class UserResponse(UserBase):
    """用户响应体。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class UserWithDepartmentResponse(UserResponse):
    """用户 + 部门信息（跨库查询用）。"""
    department: Optional["DepartmentResponse"] = None  # 前向引用，在 models/__init__.py 中 model_rebuild
