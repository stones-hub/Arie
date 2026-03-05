"""
示例一：使用 ThreadPoolExecutor（线程池）并发读取多个文件。

适用场景：
- 脚本中要同时处理多个 I/O 任务（读文件、打 HTTP、访问数据库等）
- 代码是「同步写法」，不想引入 asyncio，也能做到并发

运行方式（在项目根目录）：
    python scripts/read_files_threadpool.py app/main.py app/api/users.py
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple


def process_file(path: str) -> Tuple[str, int]:
    """
    处理单个文件的同步函数：
    - 读取文件内容
    - 统计行数
    - 返回 (路径字符串, 行数)

    关于类型标注 Tuple[str, int] 的说明：
    - Tuple[str, int] 表示「一个二元组」，长度固定为 2：
      第 0 位是 str（文件路径），第 1 位是 int（行数）。
    """
    p = Path(path)
    # read_text 是一个阻塞 I/O 操作：真正从磁盘读数据
    text = p.read_text(encoding="utf-8")
    line_count = text.count("\n") + 1 if text else 0
    return str(p), line_count


def process_files_threaded(paths: List[str], max_workers: int = 5) -> Dict[str, int]:
    """
    使用线程池并发处理多个文件，并集中回收结果。

    参数：
    - paths: 要处理的文件路径列表
    - max_workers: 最大并发线程数

    返回：
    - {路径字符串: 行数}

    关于类型标注 Dict[str, int] 的说明：
    - Dict[str, int] 表示「一个字典」，可以有 0 个或多个键值对；
      字典中所有的 key 是 str（文件路径），所有的 value 是 int（行数）。
    """
    results: Dict[str, int] = {}

    # ThreadPoolExecutor 会帮我们管理一组工作线程。
    # 这里的 with ... as ... 是「上下文管理器」语法糖，相当于：
    #
    #   executor = ThreadPoolExecutor(max_workers=max_workers)
    #   try:
    #       ...  # 使用 executor 提交任务
    #   finally:
    #       executor.shutdown(wait=True)  # 确保线程池里的线程都优雅退出
    #
    # 好处：不需要手动 shutdown，出错也能自动清理资源。这种写法不是“必须”，
    # 但对线程池、文件等需要释放资源的对象，非常推荐用 with。
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务：为每个文件创建一个 future。
        # 这一行是「字典推导式」写法：
        #
        #   future_to_path = {
        #       executor.submit(process_file, path): path
        #       for path in paths
        #   }
        #
        # 含义：
        # - executor.submit(process_file, path) 会把 process_file(path) 这个任务提交给线程池，
        #   立即返回一个 Future 对象（表示“正在执行/将要执行的任务”）。
        # - 字典的 key 是 Future，value 是对应的 path。
        # 这样后面在 as_completed(future_to_path) 里，就可以通过 future 找回原始的 path。
        future_to_path = {
            # 这里的冒号 : 是「字典中的 key: value 分隔符」：
            # - 左边 executor.submit(...) 是字典的 key（Future 对象）
            # - 右边 path 是字典的 value（对应的文件路径）
            executor.submit(process_file, path): path
            for path in paths
        }

        # as_completed 会在每个 future 完成时依次返回，谁先完成谁先回来
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                file_path, line_count = future.result()
                results[file_path] = line_count
            except Exception as exc:
                # 实际项目中可以在这里打日志，而不是直接 print
                print(f"[ERROR] 处理 {path} 时出错: {exc}")

    return results


def main(argv: List[str]) -> None:
    if not argv:
        print("用法: python scripts/read_files_threadpool.py <file1> <file2> ...")
        return

    results = process_files_threaded(argv, max_workers=5)
    for path, count in results.items():
        print(f"{path}: {count} 行")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])

