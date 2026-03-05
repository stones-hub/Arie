"""
部门相关：一张表对应一个 ORM 类，其余是 API 用 Schema（不落库）。

- ORM 模型（对应数据库表）：仅 Department，与表 department 一一对应。
- Pydantic Schema（不对应表）：DepartmentResponse，用于 API 响应体结构。
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base as OrmBase


# ---------- 仅此一个类对应数据库表 department ----------


class Department(OrmBase):
    """部门表（在部门库）。"""

    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name}>"


# ---------- Pydantic Schema，不对应表，只用于 API 响应 ----------


class DepartmentResponse(BaseModel):
    """部门响应（嵌套在用户详情等场景）。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
