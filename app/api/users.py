"""
用户相关 API：以控制器类组织路由，面向对象风格。
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db_user, get_db_dept
from app.core.log_helper import add_log
from app.models.department import DepartmentResponse
from app.models.user import UserCreate, UserResponse, UserUpdate, UserWithDepartmentResponse
from app.services.user_service import user_service
from app.services.user_read_service import user_read_service


class UserController:
    """用户资源 API 控制器，封装该资源下所有端点。"""

    def __init__(self, router: APIRouter) -> None:
        self.router = router
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.get("", response_model=list[UserResponse])(self.list_users)
        self.router.get("/{user_id}", response_model=UserResponse)(self.get_user)
        self.router.get("/{user_id}/with-department", response_model=UserWithDepartmentResponse)(self.get_user_with_department)
        self.router.post("", response_model=UserResponse, status_code=201)(self.create_user)
        self.router.put("/{user_id}", response_model=UserResponse)(self.update_user)
        self.router.delete("/{user_id}", status_code=204)(self.delete_user)

    def list_users(
        self,
        db: Session = Depends(get_db_user),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
    ) -> list[UserResponse]:
        """用户列表（分页）。"""
        users = user_service.list_users(db, skip=skip, limit=limit)
        return [UserResponse.model_validate(u) for u in users]

    def get_user(
        self,
        user_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db_user),
    ) -> UserResponse:
        """按 id 获取用户；后台执行 add_log，不阻塞响应。"""
        user = user_service.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        background_tasks.add_task(add_log, user_id, "get_user")
        return UserResponse.model_validate(user)

    def get_user_with_department(
        self,
        user_id: int,
        db_user: Session = Depends(get_db_user),
        db_dept: Session = Depends(get_db_dept),
    ) -> UserWithDepartmentResponse:
        """跨库查询：用户信息 + 关联部门（用户表在 A 库，部门表在 B 库）。"""
        user, department = user_read_service.get_user_with_department(
            db_user, db_dept, user_id
        )
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        data = UserResponse.model_validate(user).model_dump()
        data["department"] = DepartmentResponse.model_validate(department) if department else None
        return UserWithDepartmentResponse(**data)

    def create_user(self, payload: UserCreate, db: Session = Depends(get_db_user)) -> UserResponse:
        """创建用户。"""
        if user_service.get_user_by_email(db, payload.email) is not None:
            raise HTTPException(status_code=400, detail="该邮箱已注册")
        user = user_service.create_user(db, payload)
        return UserResponse.model_validate(user)

    def update_user(
        self,
        user_id: int,
        payload: UserUpdate,
        db: Session = Depends(get_db_user),
    ) -> UserResponse:
        """更新用户。"""
        user = user_service.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        if payload.email is not None:
            existing = user_service.get_user_by_email(db, payload.email)
            if existing is not None and existing.id != user_id:
                raise HTTPException(status_code=400, detail="该邮箱已被其他用户使用")
        user = user_service.update_user(db, user, payload)
        return UserResponse.model_validate(user)

    def delete_user(self, user_id: int, db: Session = Depends(get_db_user)) -> None:
        """删除用户。"""
        user = user_service.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        user_service.delete_user(db, user)


router = APIRouter(prefix="/users", tags=["users"])
UserController(router)
