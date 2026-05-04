# Python `sys` 模块总结与最佳实践

`sys` 是 Python 标准库中最核心的运行时模块之一，负责暴露解释器状态、命令行参数、标准输入输出、模块搜索路径、退出行为等底层能力。

它的特点是：

- 与解释器运行环境强相关；
- 很多功能“全局生效”，影响整个进程；
- 在脚本入口、CLI 工具、调试诊断中非常常见。

---

## 1. 常见使用场景

`sys` 主要用于：

- 读取命令行参数（`sys.argv`）；
- 退出程序并返回退出码（`sys.exit`）；
- 访问标准输入输出错误流（`sys.stdin/stdout/stderr`）；
- 调整模块搜索路径（`sys.path`）；
- 查看 Python 版本和平台信息（`sys.version`, `sys.platform`）；
- 获取解释器运行时信息（递归深度、对象大小、异常信息等）。

---

## 2. 核心对象与 API

```python
import sys
```

### 2.1 `sys.argv`：命令行参数

`sys.argv` 是一个列表：

- `sys.argv[0]`：脚本名；
- `sys.argv[1:]`：用户传入参数。

```python
import sys

print("脚本名:", sys.argv[0])
print("参数:", sys.argv[1:])
```

运行：

```bash
python main.py foo 123
```

输出类似：

```text
脚本名: main.py
参数: ['foo', '123']
```

> 实践建议：简单脚本可直接用 `sys.argv`；正式 CLI 建议使用 `argparse`。

---

### 2.2 `sys.exit()`：退出程序

`sys.exit(code)` 会抛出 `SystemExit`，终止程序。

- `code = 0`：成功；
- `code != 0`：失败（常见 1、2）。

```python
import sys

if not condition:
    print("参数错误", file=sys.stderr)
    sys.exit(2)
```

> 注意：在库代码（library）里尽量不要直接 `sys.exit`，应抛异常交给调用方处理。

---

### 2.3 `sys.stdin` / `sys.stdout` / `sys.stderr`

这三个对象分别表示：

- 标准输入；
- 标准输出；
- 标准错误输出。

```python
import sys

name = sys.stdin.readline().strip()
print(f"hello, {name}", file=sys.stdout)
print("warning message", file=sys.stderr)
```

常见用途：

- 管道式脚本；
- 区分正常输出和错误输出；
- 与 shell 重定向配合。

---

### 2.4 `sys.path`：模块搜索路径

`sys.path` 是 import 查找模块时使用的路径列表。

```python
import sys

for p in sys.path:
    print(p)
```

动态追加路径：

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
```

> 最佳实践：尽量避免在业务代码里频繁改 `sys.path`。优先使用规范包结构、虚拟环境和可安装包方式解决导入问题。

---

### 2.5 `sys.version` / `sys.version_info`

查看 Python 版本：

```python
import sys

print(sys.version)
print(sys.version_info)
```

推荐使用 `version_info` 做版本判断：

```python
if sys.version_info < (3, 10):
    raise RuntimeError("需要 Python 3.10+")
```

---

### 2.6 `sys.platform`

判断平台：

```python
import sys

if sys.platform == "win32":
    ...
elif sys.platform == "darwin":
    ...
else:
    ...
```

> 跨平台判断通常配合 `platform` 模块使用更完整。

---

### 2.7 `sys.executable`

返回当前 Python 解释器路径。

```python
import sys

print(sys.executable)
```

常用于：

- 子进程调用同一解释器；
- 诊断“到底用了哪个 Python 环境”。

---

### 2.8 `sys.modules`

当前已加载模块缓存（字典）。

```python
import sys

print("json" in sys.modules)
```

常见用途：

- 调试模块加载状态；
- 热更新/插件系统（高级场景）。

> 不建议随意修改 `sys.modules`，容易引发难排查问题。

---

### 2.9 `sys.getsizeof()`

返回对象的浅层内存大小（字节）。

```python
import sys

print(sys.getsizeof([1, 2, 3]))
```

> 注意：它不是对象“整体深层占用”。嵌套对象的总大小需要递归统计工具。

---

### 2.10 `sys.getrecursionlimit()` / `sys.setrecursionlimit()`

读取和设置递归深度限制。

```python
import sys

print(sys.getrecursionlimit())
# sys.setrecursionlimit(3000)
```

> `setrecursionlimit` 要非常谨慎。设置过大可能导致解释器崩溃（栈溢出）。

---

### 2.11 `sys.exc_info()`（异常上下文）

在异常处理中获取异常三元组：

```python
import sys

try:
    1 / 0
except Exception:
    etype, evalue, etb = sys.exc_info()
    print(etype, evalue)
```

现代 Python 中，通常直接用 `except Exception as e` 即可；`sys.exc_info()` 在框架、底层工具中仍有价值。

---

## 3. 常见实战示例

### 3.1 CLI 参数检查 + 退出码

```python
import sys

if len(sys.argv) < 2:
    print("用法: python app.py <name>", file=sys.stderr)
    sys.exit(2)

name = sys.argv[1]
print(f"hello, {name}")
sys.exit(0)
```

### 3.2 错误走 `stderr`，结果走 `stdout`

```python
import sys

def run() -> int:
    try:
        result = do_work()
        print(result, file=sys.stdout)
        return 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(run())
```

这是 CLI 脚本很推荐的结构。

### 3.3 诊断运行环境

```python
import sys

print("python:", sys.version)
print("executable:", sys.executable)
print("platform:", sys.platform)
print("path entries:", len(sys.path))
```

排查“同样代码在不同机器行为不一致”时非常有用。

---

## 4. 常见坑

### 4.1 在业务代码里滥用 `sys.path.append`

短期可用，长期会让导入关系混乱。  
建议改为：

- 正确包结构；
- `pyproject.toml` / 可安装包；
- 虚拟环境管理依赖。

### 4.2 库代码中调用 `sys.exit`

库函数里调用 `sys.exit` 会直接终止宿主进程，不利于复用和测试。  
库应抛异常，程序入口再统一 `sys.exit`。

### 4.3 把错误信息打印到 `stdout`

应使用 `stderr`，否则会污染正常输出，影响管道处理和日志采集。

### 4.4 误解 `getsizeof`

`getsizeof` 只统计对象本体，不统计深层引用对象总和。

### 4.5 随意提高递归深度

`setrecursionlimit` 不是性能优化手段，盲目调高有崩溃风险。

---

## 5. 最佳实践清单

- CLI 工具入口统一使用 `sys.exit(main())`。
- 参数解析优先 `argparse`，`sys.argv` 仅用于轻量脚本。
- 错误信息写 `sys.stderr`，结果写 `sys.stdout`。
- 使用 `sys.version_info` 做版本判断，不要解析版本字符串。
- 调试环境问题优先打印 `sys.executable`、`sys.path`、`sys.platform`。
- 避免在库层调用 `sys.exit`，改为抛异常。
- 谨慎修改 `sys.path`、`sys.modules`、递归深度。
- 对全局副作用操作（如 stdout 重定向）做好上下文管理并及时恢复。

---

## 6. `sys` 与相关模块分工建议

- 参数解析：`argparse`（优于手写 `sys.argv`）
- 环境变量：`os.environ`
- 平台信息：`platform`
- 路径处理：`pathlib`
- 日志输出：`logging`（优于 `print + sys.stderr`）
- 进程管理：`subprocess`

`sys` 更像解释器层能力入口，不建议让它承担过多业务逻辑。

---

## 7. 一句话总结

`sys` 是 Python 与解释器运行时交互的“基础总线”：  
用它做入口控制、环境诊断和 I/O 管理非常高效；但涉及全局状态的能力要克制使用、集中管理。
