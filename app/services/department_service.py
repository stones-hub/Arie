"""
部门业务逻辑：以类封装，面向对象风格，与 UserService 一致。
"""
from sqlalchemy.orm import Session

from app.models.department import Department


class DepartmentService:
    """部门业务逻辑：查部门库，与 HTTP 解耦。"""

    def get_department_by_id( self, db: Session, department_id: int) -> Department | None:
        """按 id 查询部门。"""
        return db.get(Department, department_id)

# 模块级单例，供 UserService 等使用；Session 由调用方传入
department_service = DepartmentService()
