# 获取用户时的「异步操作」与 Python 的协程/并发

## 一、需求对应关系

| 需求 | 在本项目中的做法 | 说明 |
|------|------------------|------|
| **获取用户时顺带做 add_log，但不拖慢响应** | 使用 FastAPI 的 **BackgroundTasks**，在返回响应后再执行 `add_log` | 不阻塞主请求，失败也不影响返回结果 |
| **类似 Go 的“多协程”并发** | Python 有 **asyncio 协程**；若保持当前同步 DB，可用 **ThreadPoolExecutor** 并行执行多段同步逻辑 | 见下文 |

---

## 二、add_log 不阻塞响应：BackgroundTasks

- **实现位置**：`app/core/log_helper.py` 的 `add_log(user_id, action)`，在 `app/api/users.py` 的 `get_user` 里通过 `background_tasks.add_task(add_log, user_id, "get_user")` 调用。
- **行为**：先查用户并立刻返回；**响应发出后**，FastAPI 再在同一个进程里执行 `add_log`，不阻塞当前请求。
- **注意**：`add_log` 里不要使用当前请求的 `db` Session（请求结束后 Session 会 close）；若以后要写库，应在 `add_log` 内部自己建 Session 或发到队列由 worker 写。

---

## 三、Python 里有没有“类似 Go 的协程”？

有，就是 **asyncio + async/await**，但和 Go 的 goroutine 有区别：

| 对比项 | Go goroutine | Python asyncio 协程 |
|--------|----------------------|----------------------|
| 写法 | `go fn()` | `async def` + `await`，或用 `asyncio.create_task()` |
| 调度 | 语言运行时 M:N 调度 | 单线程事件循环，协作式调度 |
| 适用场景 | CPU/IO 都可（一般用于 IO） | 主要用于 **IO 密集**（网络、文件等） |
| 多段逻辑“同时跑” | 多 goroutine 并发 | 多 coroutine 用 `asyncio.gather()` 等并发 |

所以：**Python 有协程，用法和 Go 不同，但都能做“多段 IO 并发”**。  
当前项目用的是 **同步 SQLAlchemy + 同步路由**，若要“多段逻辑同时跑”，有两种常见方式：

---

## 四、在现有同步代码里做“多段并发”

### 方式 1：ThreadPoolExecutor（适合同步 I/O）

在**同步**路由里，多段**互不依赖**的同步逻辑（如多次 DB 查询、多次 HTTP 调用）可以丢进线程池并行执行，例如：

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

_executor = ThreadPoolExecutor(max_workers=4)

def get_user_and_extra_sync(user_id: int):
    # 假设有多段同步 IO
    user = user_service.get_user_by_id(db, user_id)
    audit = audit_service.get_last_audit(db, user_id)  # 另一段同步
    return user, audit

# 在路由里（同步路由）：
# 若要把两段独立查询并行化，可：
# future1 = _executor.submit(user_service.get_user_by_id, db, user_id)
# future2 = _executor.submit(audit_service.get_last_audit, db, user_id)
# user, audit = future1.result(), future2.result()
```

注意：**同一个 DB Session 不能跨线程共享**，并行时每个任务要么用独立 Session，要么只并行非 DB 的 I/O。

### 方式 2：整条链路改成 async（asyncio 协程）

若希望用 **asyncio.gather** 做“多协程并发”，需要：

- 路由改为 `async def`；
- 数据库用 **async 驱动**（如 asyncpg、aiomysql）+ **SQLAlchemy 2.0 async**；
- 其他 I/O（HTTP、Redis）也用 async 库。

然后即可：

```python
async def get_user_rich(user_id: int):
    user_task = asyncio.create_task(get_user_async(user_id))
    audit_task = asyncio.create_task(get_audit_async(user_id))
    user, audit = await asyncio.gather(user_task, audit_task)
    return user, audit
```

当前项目若暂时不改为 async 驱动，可先沿用 **BackgroundTasks + 同步逻辑**，需要“多段并行”时再用 **ThreadPoolExecutor** 做同步任务的并行。

---

## 五、小结

- **add_log 等“事后执行、不阻塞响应”**：用 **BackgroundTasks**，已在 `get_user` 中接入。
- **Python 的协程**：用 **asyncio**（`async def` / `await` / `gather`），和 Go 的 goroutine 不同但都能做 IO 并发。
- **当前同步项目里做多段并发**：用 **ThreadPoolExecutor** 并行多段同步调用；若以后全面改为 async 再考虑 **asyncio.gather**。
