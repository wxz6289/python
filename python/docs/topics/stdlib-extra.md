# 标准库补充模块

本文覆盖日常开发中常用、但未在 [04-standard-library.md](04-standard-library.md) 详述的模块。日期时间见 [time-random.md](time-random.md)，JSON 见 [07-file-io.md](07-file-io.md)。

## 目录

- [csv — 读写表格](#csv--读写表格)
- [itertools — 迭代工具](#itertools--迭代工具)
- [subprocess — 子进程](#subprocess--子进程)
- [logging — 日志](#logging--日志)
- [pickle — 对象序列化](#pickle--对象序列化)
- [tempfile — 临时文件](#tempfile--临时文件)
- [__future__ — 未来特性](#__future__--未来特性)
- [最佳实践](#最佳实践)

## csv — 读写表格

```python
import csv

rows = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]

with open("people.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

with open("people.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        print(row["name"], row["age"])
```

| 类/函数 | 说明 |
|---------|------|
| `csv.reader` / `csv.writer` | 按行读写列表 |
| `csv.DictReader` / `DictWriter` | 按列名读写字典 |
| `newline=""` | 写入时必须，避免多余空行 |

## itertools — 迭代工具

```python
import itertools as it

print(list(it.islice(it.count(10), 5)))       # [10, 11, 12, 13, 14]
print(list(it.chain([1, 2], [3, 4])))          # [1, 2, 3, 4]
print(list(it.product("AB", repeat=2)))         # 笛卡尔积
print(list(it.combinations([1, 2, 3], 2)))      # 组合
print(list(it.permutations([1, 2, 3], 2)))      # 排列

# 分组：相邻相同 key 的元素
for key, group in it.groupby("AAABBCC"):
    print(key, list(group))
```

| 函数 | 用途 |
|------|------|
| `count` / `cycle` / `repeat` | 无限或重复序列 |
| `chain` / `chain.from_iterable` | 链接多个迭代器 |
| `islice` | 切片迭代器（惰性） |
| `groupby` | 按 key 分组（需先排序） |
| `tee` | 复制迭代器 |

## subprocess — 子进程

```python
import subprocess

result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True,
    check=False,
)
print(result.stdout, result.returncode)

# 替代 os.system()，避免 shell 注入
subprocess.run(["ls", "-la"], check=True)
```

| 参数/函数 | 说明 |
|-----------|------|
| `run(..., check=True)` | 非零退出码抛 `CalledProcessError` |
| `capture_output=True` | 捕获 stdout/stderr |
| `text=True` | 以 str 而非 bytes 返回 |
| `Popen` | 低级 API，需手动管理进程生命周期 |

**避免** `shell=True` 处理用户输入；必须用时对参数严格转义。

## logging — 日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

log.debug("detail")      # 默认不输出
log.info("started")
log.warning("slow response")
log.error("failed", exc_info=True)
```

| 级别 | 数值 | 典型用途 |
|------|------|----------|
| DEBUG | 10 | 调试细节 |
| INFO | 20 | 正常运行 |
| WARNING | 30 | 可恢复问题 |
| ERROR | 40 | 功能失败 |
| CRITICAL | 50 | 严重错误 |

生产环境用 `FileHandler` / `RotatingFileHandler` 写文件，不要用 `print` 代替日志。

## pickle — 对象序列化

```python
import pickle

data = {"scores": [90, 85], "name": "test"}

with open("state.pkl", "wb") as f:
    pickle.dump(data, f)

with open("state.pkl", "rb") as f:
    restored = pickle.load(f)
```

| 特点 | 说明 |
|------|------|
| 优点 | 保留 Python 对象类型，读写快 |
| 缺点 | 仅限 Python；**不可加载不可信来源**（可执行任意代码） |
| 替代 | 跨语言交换用 JSON；大数组用 NumPy `.npy` |

## tempfile — 临时文件

```python
import tempfile
from pathlib import Path

with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write("temp data")
    path = Path(f.name)
print(path.read_text(encoding="utf-8"))
path.unlink()

with tempfile.TemporaryDirectory() as tmpdir:
    (Path(tmpdir) / "out.txt").write_text("hello", encoding="utf-8")
# tmpdir 自动删除
```

## __future__ — 未来特性

在文件顶部导入，启用尚未成为默认行为的新语法或语义：

```python
from __future__ import annotations  # 延迟求值类型注解（Python 3.7+）

def greet(name: str) -> str:
    return f"Hello, {name}"
```

| 导入 | 效果 |
|------|------|
| `annotations` | 类型注解存为字符串，避免前向引用问题 |
| `print_function` | Python 2 兼容（已过时） |

新版本 Python 中，部分 `__future__` 导入会成为默认行为后可移除。

## 最佳实践

1. **表格数据用 `csv` 模块**，不要手动 split 逗号（字段可能含逗号或引号）。
2. **惰性/组合迭代用 `itertools`**，避免一次性 materialize 大列表。
3. **外部命令用 `subprocess.run`**，替代 `os.system()`。
4. **正式输出用 `logging`**，调试可用 `print`；设置合适级别避免生产环境刷屏。
5. **不要 pickle 不可信数据**；持久化优先考虑 JSON、SQLite 或专用格式。
