# Python 协程（async/await）标准写法速查

> 目标：看到这个文档，你能回答两个问题：
> 1. 我要写一个协程函数，标准长什么样？
> 2. 我要并发跑很多协程任务，并集中拿结果，标准长什么样？

下面所有例子都**脱离框架**（不用 FastAPI），只用标准库 `asyncio`，方便你迁移到任何脚本里。

---

## 一、最小协程：`async def` + `await`

```python
import asyncio


async def say_hello(name: str) -> None:
    """一个最简单的协程：打印两句，中间等待 1 秒。"""
    print(f"start hello {name}")
    await asyncio.sleep(1.0)  # 模拟 I/O 等待（比如读文件、打 HTTP）
    print(f"hello {name}")


async def main() -> None:
    # 在协程里调用另一个协程，必须用 await
    await say_hello("alice")


if __name__ == "__main__":
    # 标准入口：启动事件循环，跑 main 协程
    asyncio.run(main())
```

要点：

- `async def` 定义协程函数；
- 只能在 `async def` 里用 `await`；
- `asyncio.run(main())` 是脚本入口的**标准写法**。

---

## 二、标准模式 1：并发执行一堆协程任务 + 集中回收（`asyncio.gather`）

> 适用场景：有很多「结构类似、互不依赖」的 I/O 任务要一起跑，比如同时读很多文件、请求多个 HTTP 接口。

### 2.1 模板代码

```python
import asyncio
from typing import List


async def process_one(item: int) -> int:
    """
    处理「一个任务」的协程。
    这里只是 sleep 模拟 I/O，实际代码里可以是读文件、打 HTTP 等。
    """
    print(f"start {item}")
    await asyncio.sleep(1.0)  # 模拟一个耗时 I/O
    print(f"end   {item}")
    return item * 2


async def process_many(items: List[int]) -> List[int]:
    """
    标准写法：并发处理一堆任务，并集中回收结果。
    """
    # 1）为每个 item 创建一个协程任务
    tasks = [asyncio.create_task(process_one(x)) for x in items]

    # 2）并发执行所有任务，等全部完成后拿到结果列表
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return results


async def main() -> None:
    items = [1, 2, 3, 4, 5]
    results = await process_many(items)
    print("all done:", results)


if __name__ == "__main__":
    asyncio.run(main())
```

### 2.2 执行顺序说明

1. `process_many` 中创建了多个任务：`create_task(process_one(x))`；
2. `asyncio.gather(*tasks)` 会告诉事件循环：**把这些任务一起跑**；
3. 每个 `process_one` 里遇到 `await asyncio.sleep(1.0)` 就“挂起自己”，事件循环去执行其他任务；
4. 所有任务完成后，`gather` 返回一个结果列表，顺序和 `tasks` 列表一致。

**记忆方法：**

- `process_one`：一个任务怎么处理；
- `process_many`：一起跑很多任务，并 `gather` 回来。

---

## 三、标准模式 2：在协程里“包装”同步函数（`asyncio.to_thread`）

> 适用场景：你现有的处理函数是同步的（阻塞 I/O），想在协程世界里并发使用它，但暂时不想/不能改成完全 async。

### 3.1 同步版本处理函数

```python
from pathlib import Path
from typing import Tuple


def process_file_sync(path: str) -> Tuple[str, int]:
    """
    同步版本：读取文件并统计行数。
    这个函数本身不知道「协程」的存在，只是个普通阻塞函数。
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    line_count = text.count("\\n") + 1 if text else 0
    return str(p), line_count
```

### 3.2 协程包装 + 并发调度

```python
import asyncio
from typing import Dict, Iterable, Tuple


async def process_file_async(path: str) -> Tuple[str, int]:
    """
    协程包装：把同步的 process_file_sync 丢到线程池里执行。

    - asyncio.to_thread 会在线程池中执行 process_file_sync(path)；
    - 当前协程在 await 的时候可以让出控制权，去跑别的协程。
    """
    return await asyncio.to_thread(process_file_sync, path)


async def process_files_async(paths: Iterable[str]) -> Dict[str, int]:
    """
    并发处理多个文件，并集中收集结果。
    """
    # 为每个 path 创建一个协程任务
    tasks = [process_file_async(p) for p in paths]

    # gather 并发执行所有任务，全部完成后返回一个结果列表
    results = await asyncio.gather(*tasks)

    # results 是类似 [(path1, count1), (path2, count2), ...] 的列表
    return {file_path: line_count for file_path, line_count in results}
```

### 3.3 入口

```python
async def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("用法: python script.py <file1> <file2> ...")
        return

    res = await process_files_async(sys.argv[1:])
    for path, count in res.items():
        print(f"{path}: {count} 行")


if __name__ == "__main__":
    asyncio.run(main())
```

这个模式你已经在 `scripts/read_files_asyncio.py` 里用上了。

---

## 四、标准模式 3：纯 async I/O（比如读文件用 aiofiles）

> 当你依赖的库本身就是 async 版本（如 aiofiles、httpx.AsyncClient），可以不用 to_thread，直接纯 async。

```python
import asyncio
from pathlib import Path
from typing import Dict, Iterable, Tuple

import aiofiles


async def process_file_async(path: str) -> Tuple[str, int]:
    p = Path(path)
    async with aiofiles.open(p, mode="r", encoding="utf-8") as f:
        text = await f.read()
    line_count = text.count("\\n") + 1 if text else 0
    return str(p), line_count


async def process_files_async(paths: Iterable[str]) -> Dict[str, int]:
    tasks = [process_file_async(p) for p in paths]
    results = await asyncio.gather(*tasks)
    return {file_path: line_count for file_path, line_count in results}
```

和上一个模式的区别只是：不再需要 `asyncio.to_thread`，所有 I/O 调用本身就是 `await` 的。

---

## 五、什么时候要写 `await`？

可以把 `await` 理解成“**这个地方要等异步操作结果，等的时候别堵住整个线程，让事件循环去干别的事**”。

### 5.1 只能在 `async def` 里用

```python
async def foo():
    await asyncio.sleep(1)  # ✅

def bar():
    await asyncio.sleep(1)  # ❌ 语法错误：不能在普通 def 里用 await
```

### 5.2 应该 await 的对象

一般来说，只要你“调用的是 async 世界里的东西”，就应该 await：

- 协程函数的调用结果：

  ```python
  async def foo(): ...

  async def main():
      r = await foo()
  ```

- asyncio 提供的 API：`sleep` / `gather` / `to_thread` / Task 等：

  ```python
  await asyncio.sleep(1)
  result = await asyncio.to_thread(sync_func, arg)
  results = await asyncio.gather(task1, task2)
  ```

- 各种 async 库的调用（HTTP 客户端、数据库驱动等）：

  ```python
  resp = await client.get("https://example.com")
  ```

如果你忘了写 `await`，通常就等于“创建了一个协程对象但没真正执行它”，这也是常见 bug 之一。

### 5.3 「阻塞」到底阻塞了谁？（更通俗的理解）

很多人一开始会以为：`await` 一旦出现，就会像普通函数调用一样“把程序卡住等结果”。  
更准确的说法是：

- **`await` 会让「当前这个协程」停下来等结果**；
- 但在这段时间里，**事件循环/线程是空出来的，可以去跑别的协程**。

对比一下：

```python
# 同步版本：整条调用链在这里傻等，线程被卡住
result = process_file_sync(path)

# 协程版本：当前协程在这里等待，但事件循环可以先去跑别的协程
result = await process_file_async(path)
```

所以可以简单记：

> - 同步阻塞：**线程被卡住，整个程序这条线都停在这里**。  
> - `await`：**只让当前协程“暂停”，线程/事件循环继续去调度其他协程**。

当你用 `asyncio.gather(*tasks)` 一次跑很多协程时，真正的“异步并发”体现在：

- 每个协程内部看起来都在 `await` 某个 I/O；
- 事件循环却能在这些「等待中的协程」之间切换，**只要有哪个 I/O 完成，就立刻恢复对应协程去继续执行**。

因此，`await` 不是“不要等”，而是“**只让当前协程等，让 CPU 去干别的协程的事**”。 

---

## 六、一个完整协程小脚本模板（可直接拷贝改）

```python
import asyncio
from typing import List


async def process_one(item: int) -> int:
    \"\"\"处理单个任务的协程。这里用 sleep 模拟 I/O。\"\"\"
    print(f\"start {item}\")
    await asyncio.sleep(1.0)
    print(f\"end   {item}\")
    return item * 2


async def process_many(items: List[int]) -> List[int]:
    \"\"\"并发处理一组任务，并返回结果列表。\"\"\"
    tasks = [asyncio.create_task(process_one(x)) for x in items]
    results = await asyncio.gather(*tasks)
    return results


async def main() -> None:
    items = [1, 2, 3, 4, 5]
    results = await process_many(items)
    print(\"all done:\", results)


if __name__ == \"__main__\":
    asyncio.run(main())
```

你可以把这个当成“协程标准模板”：

- 填写 `process_one` 里的具体逻辑（读文件、HTTP 调用等）；
- 让 `process_many` 用 `gather` 并发跑很多个；
- 用 `asyncio.run(main())` 启动整个流程。

---

## 七、小结：写协程时的思路

1. **是否适合用协程？**
   - 是大量 I/O、要高并发 → 适合；
   - 是纯 CPU 计算 → 考虑多进程或单独服务。

2. **先写好“处理一个任务”的协程 (`process_one`)：**
   - 把所有 I/O 调用写成 `await some_async_call()`。

3. **再写“处理一堆任务”的协程 (`process_many`)：**
   - 用列表推导式或 for 循环创建一堆任务；
   - 用 `await asyncio.gather(*tasks)` 并发执行并集中拿结果。

4. **最后写入口 main + asyncio.run(main())。**

熟悉这套之后，你看到任何协程代码，都可以快速看出来：  
“这个是在定义一个任务” vs “这个是在并发跑一堆任务” vs “这个是入口”。  
然后再配合你已有的 `scripts/read_files_asyncio.py` 对照练习，会更容易真正吃透。  

