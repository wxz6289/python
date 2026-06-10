# Python 标准库速览

日常开发中最常用的标准库模块：文件操作、命令行解析、系统接口、文本处理与网络访问。

## 目录

1. [os — 操作系统接口](#os--操作系统接口)
2. [shutil — 高级文件操作](#shutil--高级文件操作)
3. [glob — 路径通配符](#glob--路径通配符)
4. [argparse — 命令行参数解析](#argparse--命令行参数解析)
5. [sys — 解释器与运行时](#sys--解释器与运行时)
6. [re — 正则表达式](#re--正则表达式)
7. [random — 伪随机数](#random--伪随机数)
8. [statistics — 基本统计](#statistics--基本统计)
9. [reprlib / pprint / textwrap](#reprlib--pprint--textwrap)
10. [urllib — 网络访问](#urllib--网络访问)
11. [最佳实践](#最佳实践)

---

## os — 操作系统接口

| 函数/属性 | 说明 |
|-----------|------|
| `os.getcwd()` | 当前工作目录 |
| `os.chdir(path)` | 切换工作目录 |
| `os.listdir(path)` | 列出目录内容 |
| `os.mkdir(path)` / `os.makedirs(path, exist_ok=True)` | 创建目录 |
| `os.remove(path)` / `os.rename(src, dst)` | 删除/重命名 |
| `os.path.join(a, b)` | 拼接路径 |
| `os.path.exists(path)` | 路径是否存在 |
| `os.environ` | 环境变量字典 |

```python
import os

print(os.getcwd())
os.makedirs("output/logs", exist_ok=True)
print(os.path.join("data", "report.csv"))
```

### 最佳实践

路径操作优先 `pathlib.Path` 或 `os.path`；避免 `os.system()`，子进程用 `subprocess`。

---

## shutil — 高级文件操作

| 函数 | 说明 |
|------|------|
| `copy(src, dst)` / `copyfile(src, dst)` | 复制文件 |
| `copytree(src, dst)` | 递归复制目录 |
| `move(src, dst)` | 移动文件或目录 |
| `rmtree(path)` | 递归删除目录 |
| `disk_usage(path)` | 磁盘使用情况 |

```python
import shutil
shutil.copyfile("source.txt", "backup.txt")
shutil.move("old.txt", "new.txt")
```

---

## glob — 路径通配符

| 模式 | 含义 |
|------|------|
| `*` | 匹配任意字符（不含 `/`） |
| `?` | 匹配单个字符 |
| `[abc]` | 匹配方括号内任一字符 |
| `**` | 递归匹配（`recursive=True`） |

```python
import glob
print(glob.glob("*.txt"))
print(glob.glob("**/*.py", recursive=True))
```

---

## argparse — 命令行参数解析

| 方法/参数 | 说明 |
|-----------|------|
| `ArgumentParser(prog, description)` | 创建解析器 |
| `add_argument(name, ...)` | 添加参数 |
| `nargs="+"` | 一个或多个值 |
| `type=int` / `default=10` | 类型转换 / 默认值 |
| `parse_args()` | 解析并返回命名空间 |

```python
import argparse

parser = argparse.ArgumentParser(prog="head", description="显示文件前几行")
parser.add_argument("filenames", nargs="+")
parser.add_argument("-n", "--lines", type=int, default=10)
args = parser.parse_args(["report.txt", "-n", "5"])
print(args.filenames, args.lines)  # ['report.txt'] 5
```

### 最佳实践

为参数添加 `help`；Jupyter 演示时向 `parse_args()` 传列表，避免触发 `SystemExit`。

---

## sys — 解释器与运行时

| 名称 | 说明 |
|------|------|
| `sys.argv` | 命令行参数（`argv[0]` 为脚本名） |
| `sys.path` | 模块搜索路径 |
| `sys.stdin/stdout/stderr` | 标准流 |
| `sys.version` / `sys.platform` | 版本 / 平台信息 |
| `sys.getsizeof(obj)` | 对象占用字节数 |

```python
import sys
print(sys.argv)
sys.stderr.write("警告：配置缺失\n")
```

---

## re — 正则表达式

| 函数 | 说明 |
|------|------|
| `search(pattern, s)` | 搜索第一个匹配 |
| `match(pattern, s)` | 从开头匹配 |
| `findall(pattern, s)` | 所有非重叠匹配 |
| `sub(pattern, repl, s)` | 替换 |
| `split(pattern, s)` | 按模式拆分 |
| `compile(pattern)` | 预编译，循环中更高效 |

```python
import re

print(re.findall(r"\bf[a-z]*", "which foot and handle feel fastest"))
# ['foot', 'feel', 'fastest']
print(re.sub(r"(\b[a-z]+) \1", r"\1", "cat in the the hat"))
# 'cat in the hat'
```

### 最佳实践

使用原始字符串 `r"..."`；复杂模式先 `compile`。

---

## random — 伪随机数

| 函数 | 说明 |
|------|------|
| `random()` | [0.0, 1.0) 浮点数 |
| `randint(a, b)` | [a, b] 整数 |
| `randrange(stop)` | 随机索引 |
| `choice(seq)` / `sample(pop, k)` | 随机选取 / 无放回抽样 |
| `shuffle(lst)` | 原地打乱 |
| `seed(n)` | 固定种子，便于复现 |

```python
import random
random.seed(42)
print(random.choice(["a", "b", "c"]), random.sample(range(100), 3))
```

---

## statistics — 基本统计

| 函数 | 说明 |
|------|------|
| `mean(data)` | 算术平均 |
| `median(data)` | 中位数 |
| `mode(data)` | 众数 |
| `stdev(data)` / `variance(data)` | 标准差 / 方差 |

```python
import statistics
data = [1.2, 2.3, 2.1, 0.9, 5.6, 3.8]
print(statistics.mean(data), statistics.median(data), statistics.variance(data))
```

---

## reprlib / pprint / textwrap

| 模块 | 用途 |
|------|------|
| `reprlib.repr(obj)` | 截断过长容器的 repr |
| `pprint.pprint(obj, width=30)` | 美化打印嵌套结构 |
| `textwrap.fill(text, width=40)` | 按宽度折行 |
| `textwrap.dedent(text)` | 去除公共前导空白 |

```python
import reprlib, pprint, textwrap

print(reprlib.repr(set("abcdefghijklmnopqrstuvwxyz")))
pprint.pprint([[[["a", "b"], "c"]]], width=20)
print(textwrap.fill("A long paragraph that needs wrapping.", width=20))
```

---

## urllib — 网络访问

| 组件 | 说明 |
|------|------|
| `urllib.request.urlopen(url, timeout=10)` | 打开 URL |
| `urllib.parse.urlparse(url)` | 解析 URL |
| `urllib.parse.urlencode(params)` | 编码查询参数 |

```python
from urllib.request import urlopen

with urlopen("https://docs.python.org/zh-cn/3/tutorial/stdlib.html", timeout=10) as resp:
    for line in resp:
        text = line.decode("utf-8")
        if "互联网访问" in text:
            print(text.rstrip())
```

### 最佳实践

生产环境优先 `requests` / `httpx`；`urlopen` 必须设 `timeout` 并处理 `URLError`。

---

## 最佳实践

| 原则 | 说明 |
|------|------|
| 按需导入 | `import os`，避免 `from os import *` |
| 优先 pathlib | `pathlib.Path` 替代部分 `os.path` |
| 正则预编译 | 循环中重复使用时 `re.compile()` |
| 随机可复现 | 测试用 `random.seed()` |
| 网络有超时 | 避免无限阻塞 |
| 查阅文档 | `help(func)`、`dir(module)` 探索 API |

完整列表见 [Python 标准库索引](https://docs.python.org/zh-cn/3/library/index.html)。
