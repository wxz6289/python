# 文件 I/O

## 目录

- [概述](#概述)
- [open() 与文件模式](#open-与文件模式)
- [with 语句（推荐）](#with-语句推荐)
- [读取操作](#读取操作)
- [写入操作](#写入操作)
- [seek 与 tell 定位](#seek-与-tell-定位)
- [编码：始终指定 UTF-8](#编码始终指定-utf-8)
- [pathlib 路径操作（推荐）](#pathlib-路径操作推荐)
- [JSON 序列化](#json-序列化)
- [常用 os / shutil 操作](#常用-os--shutil-操作)
- [最佳实践](#最佳实践)

## 概述

Python 通过内置 `open()` 函数操作文件。文件是 I/O 资源，必须在使用后关闭，否则可能导致数据丢失或文件句柄泄漏。

**核心原则**：优先使用 `with` 语句自动管理文件生命周期，并始终显式指定 `encoding="utf-8"`。

## open() 与文件模式

```python
f = open("data.txt", mode="r", encoding="utf-8")
# ... 操作 ...
f.close()  # 手动关闭（不推荐，见 with 语句）
```

### 模式字符

| 模式 | 含义 |
|------|------|
| `r` | 只读（默认）；文件不存在则报错 |
| `w` | 写入；**文件存在则清空** |
| `x` | 独占创建；文件已存在则报错 |
| `a` | 追加；写入内容追加到文件末尾 |
| `b` | 二进制模式（如 `rb`、`wb`） |
| `t` | 文本模式（默认） |
| `+` | 读写（如 `r+`、`w+`） |

### 常见组合

```python
open("f.txt", "r")     # 只读文本
open("f.txt", "w")     # 写入（清空原内容）
open("f.txt", "a")     # 追加
open("f.bin", "rb")    # 只读二进制
open("f.txt", "r+")    # 读写，不截断；文件必须存在
open("f.txt", "w+")    # 读写，**会清空**文件
```

**`r+` 与 `w+` 的区别**：`w+` 打开时会清空文件内容；`r+` 保留原内容但要求文件已存在。

## with 语句（推荐）

`with` 语句是上下文管理器语法，离开块时**自动关闭**文件，即使发生异常也会执行。协议细节见 [11-context-managers.md](11-context-managers.md)。

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
# 此处 f 已自动关闭
```

等价于：

```python
f = open("data.txt", "r", encoding="utf-8")
try:
    content = f.read()
finally:
    f.close()
```

`with` 更简洁、更安全，是文件操作的**首选写法**。

## 读取操作

```python
with open("data.txt", "r", encoding="utf-8") as f:
    # 一次读取全部内容
    whole = f.read()

    # 读取指定字节/字符数
    chunk = f.read(100)

    # 读取一行（含换行符）
    line = f.readline()

    # 读取所有行到列表
    lines = f.readlines()

    # 逐行迭代（内存友好，推荐大文件使用）
    for line in f:
        print(line.rstrip("\n"))
```

按行读取大文件的推荐方式：

```python
with open("large.log", "r", encoding="utf-8") as f:
    for line in f:
        process(line)
```

## 写入操作

```python
lines = ["第一行\n", "第二行\n", "第三行\n"]

with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello\n")
    f.write("World\n")
    f.writelines(lines)  # 写入序列，不自动添加换行符
    f.flush()            # 强制刷新缓冲区（通常 close 时自动执行）
```

追加写入：

```python
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("新日志条目\n")
```

## seek 与 tell 定位

文件有读写位置指针，可通过 `seek()` 移动、`tell()` 查询：

```python
import io

with open("data.txt", "r+", encoding="utf-8") as f:
    f.write("0123456789")
    f.seek(5)              # 移动到第 5 个字符（从 0 开始）
    f.write("HELLO")
    pos = f.tell()         # 当前位置
    print(pos)

    f.seek(0)              # 回到开头
    print(f.read())
```

`whence` 参数（第三个参数）：

| 值 | 常量 | 含义 |
|----|------|------|
| `0` | `io.SEEK_SET` | 相对文件开头（默认） |
| `1` | `io.SEEK_CUR` | 相对当前位置 |
| `2` | `io.SEEK_END` | 相对文件末尾 |

**注意**：文本模式下 `seek` 行为因平台和编码而异，二进制模式更可靠。

## 编码：始终指定 UTF-8

Python 3 文本模式默认编码取决于系统 locale，跨平台时可能不一致。**始终显式指定**：

```python
# 推荐
with open("中文.txt", "r", encoding="utf-8") as f:
    text = f.read()

with open("中文.txt", "w", encoding="utf-8") as f:
    f.write("你好，世界")

# 写入 BOM 标记的 UTF-8（部分 Windows 程序需要）
with open("data.csv", "w", encoding="utf-8-sig") as f:
    f.write("name,age\n")
```

处理无法解码的字节时，可指定错误策略：

```python
with open("raw.bin", "r", encoding="utf-8", errors="replace") as f:
    text = f.read()  # 非法字节替换为 �
```

常用 `errors` 值：`"strict"`（默认）、`"ignore"`、`"replace"`、`"backslashreplace"`。

## pathlib 路径操作（推荐）

`pathlib.Path` 提供面向对象的路径 API，跨平台、可读性更好，**优于字符串拼接**：

```python
from pathlib import Path

# 构建路径
data_dir = Path("project") / "data"
file_path = data_dir / "report.txt"

# 读写文件（Python 3.5+）
content = file_path.read_text(encoding="utf-8")
file_path.write_text("新内容\n", encoding="utf-8")

# 路径信息
print(file_path.name)       # report.txt
print(file_path.stem)       # report
print(file_path.suffix)     # .txt
print(file_path.parent)     # project/data
print(file_path.exists())   # True/False
print(file_path.resolve())  # 绝对路径

# 遍历目录
for py_file in Path("src").rglob("*.py"):
    print(py_file)

# 创建目录
data_dir.mkdir(parents=True, exist_ok=True)
```

`pathlib` 与 `with open()` 可组合使用：

```python
path = Path("config.json")
with path.open("r", encoding="utf-8") as f:
    data = f.read()
```

## JSON 序列化

JSON 适合跨语言数据交换，仅支持基本类型（dict、list、str、int、float、bool、None）：

```python
import json
from pathlib import Path

path = Path("data.json")

# 读取
with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

# 修改并写回
data["phone"] = "13800000000"
with path.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 字符串与对象互转
text = json.dumps(data, ensure_ascii=False)
restored = json.loads(text)
```

`ensure_ascii=False` 保留中文等非 ASCII 字符；`indent=2` 格式化输出。

## 常用 os / shutil 操作

目录遍历用 `os.walk()`；复制/移动/删除分别用 `shutil.copy()`、`shutil.move()`、`shutil.rmtree()`。新代码优先用 `pathlib`，仅在需要时再配合 `os`/`shutil`。

## 最佳实践

1. **始终用 `with` 打开文件**，不要依赖手动 `close()`。
2. **始终指定 `encoding="utf-8"`**，避免平台默认编码带来的乱码问题。
3. **路径操作用 `pathlib.Path`**，避免 `os.path.join` 与字符串 `/` 混用。
4. **大文件逐行迭代**，不要用 `read()` 或 `readlines()` 一次性加载到内存。
5. **写模式谨慎使用 `w`/`w+`**，它们会清空已有内容；不确定时用 `a` 或先备份。
6. **二进制与文本分开处理**：图片、压缩包等用 `"rb"`/`"wb"`，不要当文本读写。
7. **JSON 用 `ensure_ascii=False`** 保存中文；需要跨语言交换时优先 JSON 而非 pickle。
8. **检查文件是否存在**：`Path.exists()` 或 `Path.is_file()`，而非直接 `open` 后捕获异常（除非预期文件可能不存在）。
