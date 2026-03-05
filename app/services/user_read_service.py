"""
组合查询服务（Application Service）：跨多个资源的只读查询。

本模块依赖下层的 UserService、DepartmentService，但自身不直接做持久化，
只负责编排和组装不同服务的数据（例如「用户 + 部门」）。
"""
from typing import Tuple

from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.user import User
from app.services.department_service import department_service
from app.services.user_service import user_service


class UserReadService:
    """与用户相关的组合查询（跨库 / 跨资源）。"""

    def get_user_with_department(
        self,
        db_user: Session,
        db_dept: Session,
        user_id: int,
    ) -> Tuple[User | None, Department | None]:
        """
        跨库查询：从用户库取用户、从部门库取部门，组合返回 (user, department)。
        """
        user = user_service.get_user_by_id(db_user, user_id)
        if user is None:
            return None, None

        department: Department | None = None
        if user.department_id is not None:
            department = department_service.get_department_by_id(
                db_dept, user.department_id
            )
        return user, department


# 模块级单例，供 API 层使用
user_read_service = UserReadService()

