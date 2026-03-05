"""
多数据源：每个库独立 engine + Session，各自维护连接池。
用户表与部门表可落在不同库（A/B），同一请求内注入多个 Session 分别访问。
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config.settings import settings

# 用户库 / 部门库 URL，未单独配置则回退到 database_url（单库场景）
_url_user = settings.database_url_user or settings.database_url
_url_dept = settings.database_url_dept or settings.database_url


def _engine(url: str) -> Engine:
    """
    根据连接串创建一个 SQLAlchemy Engine（含连接池）。

    传参
    ----
    url : str
        数据库连接串。例如：
        - sqlite:///./app.db
        - mysql+pymysql://user:pass@host:3306/dbname?charset=utf8mb4

    函数内逻辑
    ----------
    - connect_args：仅 SQLite 时设置 check_same_thread=False，允许多线程共用同一连接
      （SQLite 默认只允许创建连接的线程使用，FastAPI 多线程下会报错）。
    - create_engine 的常用参数：
      - pool_size=5：连接池常驻连接数
      - max_overflow=10：超出 pool_size 时最多再创建的连接数
      - pool_pre_ping=True：从池中取连接前先 ping，断线则重连，避免使用失效连接
      - echo=settings.debug：为 True 时把 SQL 打印到控制台，便于调试
    """
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(
        url,
        connect_args=connect_args,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=settings.debug,
    )


engine_user = _engine(_url_user)
engine_dept = _engine(_url_dept)

# Session 工厂：调用 SessionUserLocal() 会生成一个绑定到对应 engine 的新 Session
# autocommit=False：需显式 commit 才提交；autoflush=False：不自动把未提交变更刷成 SQL（按需 flush/commit）
# bind=engine_xxx：该 Session 使用的连接来自哪个库的连接池
SessionUserLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_user)
SessionDeptLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_dept)

# 兼容旧用法：单库时与用户库一致
engine = engine_user
SessionLocal = SessionUserLocal


class Base(DeclarativeBase):
    """
    ORM 声明式基类，所有表模型必须继承此类。

    Base 在项目里的用法只有三处，且都不在 service 里「显式写 Base」：

    1) 模型定义时继承（models/user.py、models/department.py）
       class User(OrmBase):   # OrmBase 就是本 Base
       class Department(OrmBase):
       这样 SQLAlchemy 才知道 User/Department 是「表」，并纳入同一套 metadata。

    2) 建表时用 metadata（main.py lifespan）
       Base.metadata.create_all(bind=engine_user, tables=[User.__table__])
       所有继承 Base 的模型的 __table__ 都在 Base.metadata 里。

    3) 实例上的通用方法（在 service/其他地方用到的是「对象」）
       user = db.get(User, 1)   # user 是 User 实例，User 继承 Base
       user.to_dict()           # 来自 Base，可打日志、调试
       repr(user)               # 若子类没写 __repr__，会用 Base 的
       Service 里拿到的都是「子类实例」，所以可以随时调这些基类方法。
    """

    def __repr__(self) -> str:
        """子类未覆盖时沿用：按主键展示。"""
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__} id={pk}>"

    def to_dict(self) -> dict:
        """所有子类实例都可调：当前行的列名→值，便于日志或简单序列化。"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
