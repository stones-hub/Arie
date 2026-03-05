"""
FastAPI 应用入口：创建 app、挂载路由。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.users import router as users_router
from app.config.settings import settings
from app.db.session import Base, engine_user, engine_dept
from app.models.department import Department
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：按库建表（用户表→用户库，部门表→部门库），关闭时释放连接池。"""
    Base.metadata.create_all(bind=engine_user, tables=[User.__table__])
    Base.metadata.create_all(bind=engine_dept, tables=[Department.__table__])
    yield
    engine_user.dispose()
    engine_dept.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Hello, Web API"}


@app.get("/health")
def health():
    return {"status": "ok"}
