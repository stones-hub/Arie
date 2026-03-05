"""
示例二：使用 ProcessPoolExecutor（进程池）并发处理多个「相对耗 CPU」的任务。

说明：
- 对单纯的“读文件”来说，多进程通常意义不大（I/O 为主，线程就够了）；
- 这里为了演示多进程的写法，假设在读取文件后还有一段「重计算」。

运行方式（在项目根目录）：
    python scripts/read_files_processpool.py app/main.py app/api/users.py
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple


def heavy_compute(text: str) -> int:
    """
    模拟一个 CPU 密集计算，例如：
    - 大量统计
    - 加解密
    - 压缩/解压 等

    这里只是简单地做一些字符串操作来消耗一点 CPU。
    """
    # 很简单的“假计算”：统计所有非空白字符数量
    return sum(1 for ch in text if not ch.isspace())


def process_file_cpu_heavy(path: str) -> Tuple[str, int, int]:
    """
    进程池中的任务函数：
    - 读取文件
    - 统计行数
    - 做一次“重计算”（字符统计）
    返回 (路径, 行数, 统计值)
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    line_count = text.count("\n") + 1 if text else 0
    score = heavy_compute(text)
    return str(p), line_count, score


def process_files_multiprocess(
    paths: List[str], max_workers: int = 4
) -> Dict[str, Tuple[int, int]]:
    """
    使用多进程并发处理多个文件。

    参数：
    - paths: 文件路径列表
    - max_workers: 最大进程数

    返回：
    - {路径: (行数, 统计值)}
    """
    results: Dict[str, Tuple[int, int]] = {}

    # 注意：多进程适合 CPU 密集型任务，这里只是示例
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(process_file_cpu_heavy, path): path for path in paths
        }

        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                file_path, line_count, score = future.result()
                results[file_path] = (line_count, score)
            except Exception as exc:
                print(f"[ERROR] 处理 {path} 时出错: {exc}")

    return results


def main(argv: List[str]) -> None:
    if not argv:
        print("用法: python scripts/read_files_processpool.py <file1> <file2> ...")
        return

    results = process_files_multiprocess(argv, max_workers=4)
    for path, (line_count, score) in results.items():
        print(f"{path}: {line_count} 行, score={score}")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])

