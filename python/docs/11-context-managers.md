# 上下文管理器

上下文管理器保证资源（文件、锁、连接等）在代码块结束后被正确释放，即使发生异常也不例外。`with` 语句是其语法糖。

## 目录

1. [with 语句基础](#with-语句基础)
2. [上下文管理器协议](#上下文管理器协议)
3. [contextlib 工具](#contextlib-工具)
4. [常见内置上下文管理器](#常见内置上下文管理器)
5. [最佳实践](#最佳实践)

---

## with 语句基础

进入 `with` 块时调用 `__enter__`，离开时（正常或异常）调用 `__exit__`：

```python
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
# 文件已自动关闭
```

多个上下文管理器可写在一行：

```python
with open("src.txt", encoding="utf-8") as src, open("dst.txt", "w", encoding="utf-8") as dst:
    dst.write(src.read())
```

详见 [07-file-io.md](07-file-io.md) 中的文件 I/O 示例。

---

## 上下文管理器协议

类实现 `__enter__` 与 `__exit__` 即可作为上下文管理器：

```python
class ManagedResource:
    def __enter__(self):
        print("acquire")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("release")
        return False  # False/None：异常继续传播；True：抑制异常


with ManagedResource() as r:
    print("using", r)
```

| 参数 | 说明 |
|------|------|
| `exc_type` | 异常类型；无异常时为 `None` |
| `exc_val` | 异常实例 |
| `exc_tb` | traceback 对象 |
| 返回值 | `True` 表示"已处理异常"，不再向上抛出 |

---

## contextlib 工具

### @contextmanager 装饰器

用生成器快速定义上下文管理器，`yield` 之前相当于 `__enter__`，之后相当于 `__exit__`：

```python
from contextlib import contextmanager


@contextmanager
def managed_resource(name):
    print(f"setup {name}")
    try:
        yield name
    finally:
        print(f"teardown {name}")


with managed_resource("db") as name:
    print(f"work with {name}")
```

### 其他常用 API

| API | 用途 |
|-----|------|
| `contextlib.closing(obj)` | 退出时调用 `obj.close()` |
| `contextlib.suppress(*exc)` | 忽略指定异常 |
| `contextlib.redirect_stdout(f)` | 重定向 stdout |
| `ExitStack` | 动态管理多个上下文管理器 |

```python
from contextlib import suppress, ExitStack

with suppress(FileNotFoundError):
    open("missing.txt").read()

with ExitStack() as stack:
    files = [stack.enter_context(open(f"part{i}.txt")) for i in range(3)]
    # 全部文件在退出时自动关闭
```

---

## 常见内置上下文管理器

| 对象 | 释放行为 |
|------|----------|
| 文件对象 | 关闭文件句柄 |
| `threading.Lock` | 释放锁 |
| `decimal.localcontext()` | 恢复 decimal 精度上下文 |
| `unittest.mock.patch` | 撤销 mock |
| `tempfile.TemporaryDirectory()` | 删除临时目录 |

异步上下文管理器实现 `__aenter__` / `__aexit__`，配合 `async with` 使用，详见 [asyncio 专题](../asyncio/asyncio.md)。

---

## 最佳实践

1. **管理资源优先 `with`**，不要依赖 `__del__` 或手动 `close()`。
2. **清理逻辑放 `finally` 或 `__exit__`**，确保异常时也能执行。
3. **`__exit__` 中不要吞掉不该吞的异常**，仅在明确需要时返回 `True`。
4. **复杂 setup/teardown 用 `@contextmanager`**，比写完整类更简洁。
5. **需要多个动态资源时用 `ExitStack`**，避免嵌套过深的 `with`。
