"""
示例三：使用 asyncio（协程）并发读取多个文件。

说明：
- 这里用的是 asyncio + to_thread 的方式：保留同步的读文件函数，
  但通过协程调度，让多个文件的读取「同时进行」。
- 对你来说，这个示例最接近 Go 里「开很多 goroutine 读文件」的感觉。

运行方式（在项目根目录）：
    python scripts/read_files_asyncio.py app/main.py app/api/users.py
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, Iterable, Tuple


def process_file_sync(path: str) -> Tuple[str, int]:
    """
    同步版的读取 + 行数统计函数：
    - 读取文件内容
    - 统计行数
    - 返回 (路径字符串, 行数)

    注意：这个函数本身是同步阻塞的。
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    line_count = text.count("\n") + 1 if text else 0
    return str(p), line_count


async def process_file_async(path: str) -> Tuple[str, int]:
    """
    协程包装：把同步的 process_file_sync 放到线程池里执行。

    - asyncio.to_thread 会把阻塞的函数丢给后台线程池执行，
      当前协程在等待时可以让出控制权，去跑别的协程。
    """
    return await asyncio.to_thread(process_file_sync, path)


async def process_files_async(paths: Iterable[str]) -> Dict[str, int]:
    """
    使用 asyncio 并发处理多个文件：
    - 为每个文件创建一个协程任务
    - 用 asyncio.gather 并发执行
    - 集中收集结果
    """
    tasks = [process_file_async(p) for p in paths]

    # gather 会并发执行所有任务，并在全部完成后返回结果列表
    results = await asyncio.gather(*tasks, return_exceptions=False)

    return {file_path: line_count for file_path, line_count in results}


async def main(argv: list[str]) -> None:
    if not argv:
        print("用法: python scripts/read_files_asyncio.py <file1> <file2> ...")
        return

    results = await process_files_async(argv)
    for path, count in results.items():
        print(f"{path}: {count} 行")


if __name__ == "__main__":
    import sys

    asyncio.run(main(sys.argv[1:]))

