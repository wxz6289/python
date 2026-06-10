# sys 与 os

`sys` 模块与 Python 解释器交互；`os` 模块提供操作系统接口（文件、进程、环境变量等）。

## 目录

- [sys 模块](#sys-模块)
- [os 模块](#os-模块)
- [fileinput 模块](#fileinput-模块)
- [最佳实践](#最佳实践)

## sys 模块

| 属性/函数 | 说明 |
|-----------|------|
| `argv` | 命令行参数列表（`argv[0]` 为脚本名） |
| `path` | 模块搜索路径列表 |
| `platform` | 平台标识（如 `darwin`、`linux`） |
| `modules` | 已加载模块字典 |
| `exit([code])` | 退出程序 |
| `stdin` / `stdout` / `stderr` | 标准流对象 |

```python
import sys

print(sys.platform)
print(sys.argv)
```

### 处理命令行参数

```python
import sys

args = sys.argv[1:]
args.reverse()
print(":".join(args))
```

> 复杂命令行解析推荐使用 `argparse` 模块。

## os 模块

提供文件/目录操作、进程管理、环境变量访问等。

| 属性/函数 | 说明 |
|-----------|------|
| `environ` | 环境变量映射 |
| `system(cmd)` | 在子 shell 中执行命令 |
| `sep` / `pathsep` | 路径分隔符 / 搜索路径分隔符 |
| `linesep` | 行分隔符 |
| `name` | 操作系统名称（`posix`、`nt` 等） |
| `getcwd()` / `chdir()` | 获取/切换工作目录 |
| `listdir()` / `mkdir()` / `remove()` | 文件与目录操作 |

```python
import os

print(os.name, os.sep)
# print(os.environ.get("HOME"))
# print(os.getcwd())
```

> **路径操作**优先使用 `pathlib.Path`，比 `os.path` 更直观。执行外部命令推荐 `subprocess` 而非 `os.system()`。

### 打开浏览器

```python
import webbrowser

webbrowser.open("https://python.org")
```

## fileinput 模块

方便地迭代一个或多个输入流（文件或 stdin）中的行。

| 函数/方法 | 说明 |
|-----------|------|
| `input([files[, inplace[, backup]]])` | 迭代行 |
| `filename()` | 当前文件名 |
| `lineno()` | 累计行号 |
| `filelineno()` | 当前文件内行号 |
| `isfirstline()` | 是否为当前文件首行 |
| `isstdin()` | 是否来自 stdin |
| `nextfile()` | 关闭当前文件，跳到下一个 |
| `close()` | 关闭序列 |

```python
import fileinput

for line in fileinput.input():
    print(fileinput.filename(), fileinput.lineno(), line.rstrip())
```

## 最佳实践

1. **路径一律用 `pathlib`**：`Path("dir") / "file.txt"`。
2. **子进程用 `subprocess.run()`**，避免 `os.system()` 的安全与可移植问题。
3. **环境变量**用 `os.environ.get("KEY", default)`，缺失时不抛异常。
4. **跨平台**时注意 `os.name`、`sys.platform`，不要硬编码路径分隔符。
5. **命令行工具**用 `argparse`，`sys.argv` 仅适合极简场景。
6. **批量处理文件**时 `fileinput` 可透明处理多文件和 inplace 编辑。
