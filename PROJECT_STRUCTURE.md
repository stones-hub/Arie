# Aries Web API 项目结构与运行说明

## 实际目录结构

```text
Aries/
├── app/                      # 应用主包
│   ├── __init__.py
│   ├── main.py               # FastAPI 应用入口，挂载路由
│   ├── api/                  # API 路由层（如 users 接口）
│   ├── config/               # 配置集中管理（环境变量、端口、DB 连接等）
│   ├── core/                 # 公共依赖、日志等核心能力
│   ├── db/                   # 数据库连接、Session、Base
│   ├── models/               # ORM 模型与 Pydantic Schema
│   └── services/             # 业务逻辑层（user/department 等）
├── docs/                     # 设计文档、SQL DDL 与示例数据
├── scripts/                  # 辅助脚本（读文件并发示例等）
├── run.py                    # 启动脚本（开发环境快捷启动）
├── requirements.txt          # 项目依赖清单（用于 pip 安装）
├── .env                      # 环境变量配置（本地/线上共用模板，可按需复制）
└── .venv/                    # 本地虚拟环境目录（通常不提交到 Git）
```

> 说明：`tests/` 目录目前尚未创建，后续如需要可按惯例新增，专门存放单元测试与接口测试。

---

## 各目录与关键文件用途说明

| 路径 | 用途 | 典型内容 |
|------|------|----------|
| **app/** | 应用主包，所有业务代码的根目录 | `main.py`、`api/`、`config/`、`core/`、`models/`、`services/`、`db/` |
| **app/main.py** | FastAPI 应用入口，挂载路由、配置生命周期 | 创建 `app = FastAPI(...)`，在 lifespan 中按库建表，注册 `users` 路由，提供 `/` 与 `/health` 等基础接口 |
| **app/api/** | **API 路由层**：HTTP 端点定义 | 如 `users.py` 暴露用户查询接口，调用对应 service 完成业务 |
| **app/services/** | **业务逻辑层**：与 HTTP 解耦的业务实现 | `user_service.py`、`department_service.py` 等，内部操作数据库、组装模型、做校验等 |
| **app/models/** | **数据模型与 ORM**：表模型与请求/响应 Schema | `user.py`、`department.py` 等，与 `docs/ddl_and_seed.sql` 中表结构一致 |
| **app/db/** | **数据库与 Session 管理** | `session.py` 定义多数据源 engine 与 `SessionUserLocal`、`SessionDeptLocal`，支持单库/多库切换 |
| **app/config/settings.py** | **集中配置**：从 `.env` / 环境变量加载 Settings | 包含 `app_name`、`debug`、`port`、`database_url` / `database_url_user` / `database_url_dept` 等字段 |
| **app/core/** | **核心公共能力**：日志、依赖注入等 | 如 `log_helper.py`、`deps.py`，对外提供依赖注入函数与统一日志接口 |
| **docs/** | 项目设计与说明文档 | ORM 设计、会话模式、异步并发说明、DDL 与种子数据等 |
| **docs/ddl_and_seed.sql** | 用户与部门表的 MySQL DDL 与示例数据 | 在目标 MySQL 库中执行，可一次性建表并插入一些演示数据 |
| **scripts/** | 额外示例脚本 | `read_files_threadpool.py` / `asyncio` / `processpool` 等并发读文件示例 |
| **requirements.txt** | Python 依赖清单 | 如 `fastapi`、`uvicorn[standard]`、`sqlalchemy`、`pydantic-settings` 等第三方包 |
| **.env** | 环境变量配置文件 | 配置 `APP_NAME`、`DEBUG`、`DATABASE_URL`、`DATABASE_URL_USER`、`DATABASE_URL_DEPT` 等 |
| **run.py** | 启动脚本（偏开发） | 从 `settings` 读取端口，调用 `uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)` 启动 |

---

## 依赖管理与 `requirements.txt`

- **依赖来源分类**
  - **标准库**：如 `os`、`sys`、`pathlib` 等，不需要写进 `requirements.txt`。
  - **项目自有代码**：如 `app/`、`scripts/` 里的模块，也不需要写进 `requirements.txt`。
  - **第三方库**：如 `fastapi`、`uvicorn`、`sqlalchemy`、`pydantic-settings`、`email-validator`、`pymysql` 等，**必须通过 pip 安装，并写进 `requirements.txt`**。

- **新增第三方依赖时的推荐流程**
  1. 在当前虚拟环境中安装依赖，例如：
     ```bash
     pip install some-package
     ```
  2. **更新 `requirements.txt`**，保持与实际环境一致，有两种方式：
     - 精细手动维护：直接在 `requirements.txt` 中追加或修改一行，例如：
       ```text
       some-package==1.2.3
       ```
     - 或使用 `pip freeze` 全量覆盖（适合个人或小项目）：
       ```bash
       pip freeze > requirements.txt
       ```
  3. 提交代码时，**记得一并提交更新后的 `requirements.txt`**，以便他人或线上环境能用同一套依赖重建环境。

- **不用写入 `requirements.txt` 的情况**
  - 只使用标准库。
  - 只新增了本项目内部的模块/包（例如新增 `app/services/order_service.py`）。

---

## 本地开发运行

1. **创建并激活虚拟环境（推荐放在项目根目录 `.venv/` 下）**

   - 使用 **uv**（推荐）：

     ```bash
     cd Aries
     uv venv .venv
     source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
     ```

   - 或使用内置 `venv`（不依赖 uv）：

     ```bash
     cd Aries
     python -m venv .venv
     source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
     ```

2. **安装依赖**

   - 使用 **uv**：

     ```bash
     uv pip install -r requirements.txt
     ```

   - 或使用 `pip`：

     ```bash
     pip install -r requirements.txt
     ```

3. **配置环境变量（编辑 `.env`）**

   - 默认配置示例：
     - `APP_NAME=Web API`
     - `DEBUG=false`
     - `DATABASE_URL=sqlite:///./app.db`（开发环境可先使用 SQLite）
     - 需要使用 MySQL 多库时，配置：
       - `DATABASE_URL_USER=mysql+pymysql://root:密码@host:3306/库名?charset=utf8mb4`
       - `DATABASE_URL_DEPT=mysql+pymysql://root:密码@host:3306/库名?charset=utf8mb4`

4. **（可选）初始化 MySQL 表结构和测试数据**

   - 在目标 MySQL 数据库中执行 `docs/ddl_and_seed.sql`：
     - 建立 `department` 与 `user` 表；
     - 插入若干演示部门与用户数据，便于直接调用接口验证。

5. **启动开发服务**

   - 使用提供的 `run.py`（带自动重载，适合本地开发）：
     ```bash
     python run.py
     ```
   - 或直接使用 uvicorn（显式指定 host/port）：
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```

   启动后可访问：

   - `http://127.0.0.1:8000/`：根路由，返回简单问候。
   - `http://127.0.0.1:8000/health`：健康检查。
   - `http://127.0.0.1:8000/docs`：Swagger UI 接口文档。

---

## 线上部署与运行（生产环境）

> 目标：在 Linux 服务器上部署 Aries Web API，使用稳定的 Python 虚拟环境与数据库连接，关闭自动重载，并使用多 worker 提升并发能力。

1. **准备运行环境**
   - 安装 Python 3.10+。
   - 创建独立系统用户和目录（可选，按公司规范）。
   - 将项目代码部署到如 `/opt/aries` 目录。

2. **创建虚拟环境并安装依赖**

   ```bash
   cd /opt/aries
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **配置 `.env`（生产环境专用）**

   - 建议单独维护一份生产配置，例如 `.env.prod`，内容类似：
     ```text
     APP_NAME=Aries Web API
     DEBUG=false
     APP_PORT=8000
     DATABASE_URL_USER=mysql+pymysql://user:pass@db-host:3306/user_db?charset=utf8mb4
     DATABASE_URL_DEPT=mysql+pymysql://user:pass@db-host:3306/dept_db?charset=utf8mb4
     ```
   - 部署时可直接将其重命名/复制为 `.env`，或通过环境变量覆盖。

4. **初始化数据库**

   - 在对应 MySQL 库中执行 `docs/ddl_and_seed.sql`（如需测试数据）。
   - 确保 `DATABASE_URL_USER` 和 `DATABASE_URL_DEPT` 指向的库中已存在这些表。
   - 应用启动时，`app/main.py` 的 lifespan 会根据模型再次 `create_all`，保证表存在。

5. **使用 uvicorn 启动生产服务（关闭 reload，多 worker）**

   - 推荐在虚拟环境中使用如下命令：
     ```bash
     cd /opt/aries
     source .venv/bin/activate
     uvicorn app.main:app \
       --host 0.0.0.0 \
       --port 8000 \
       --workers 4
     ```
   - **注意**：生产环境不建议开启 `--reload`，避免频繁重启影响性能与稳定性。

6. **配合进程管理/反向代理（可选但推荐）**

   - 使用 `systemd` 管理 uvicorn 进程，配置自动重启与日志。
   - 或使用 Nginx 作为反向代理：
     - 外部请求 → Nginx（443/80）→ uvicorn（8000）。
     - Nginx 负责 TLS 终止、限流、基本安全策略。

7. **依赖更新与上线流程建议**

   - 新增第三方包 → 在测试环境中先更新虚拟环境与 `requirements.txt` → 通过测试后再同步到生产。
   - 生产环境更新依赖时，务必重新运行：
     ```bash
     pip install -r requirements.txt
     # 然后重启 uvicorn / systemd 服务
     ```

通过以上约定，`PROJECT_STRUCTURE.md` 同时起到：

- 描述当前 Aries 项目的**真实目录结构与职责划分**；
- 规范如何**维护 `requirements.txt` 与第三方依赖**；
- 指导如何在本地与线上环境中**启动与运行**该 Web API。
