# 输出与字符串格式化

本文涵盖 `print`、常用内置函数与语句，以及 Python 字符串格式化的主要方式。

## 目录

- [print 函数](#print-函数)
- [内置函数与 import](#内置函数与-import)
- [解包与赋值](#解包与赋值)
- [条件与循环](#条件与循环)
- [字符串格式化](#字符串格式化)
- [pass、del、exec、eval](#passdelexeceval)
- [match 语句](#match-语句)
- [最佳实践](#最佳实践)

## print 函数

`print` 将参数转为字符串输出，默认以空格分隔、换行结尾。

```python
greeting = "hello"
print(greeting, "world")              # hello world
print(greeting, "world", sep="*")     # hello*world
print(greeting, "world", end="!\n")   # 自定义结尾
```

## 内置函数与 import

| 函数/语句 | 说明 |
|-----------|------|
| `chr(n)` / `ord(c)` | 码点 ↔ 字符 |
| `enumerate(seq)` | 带索引迭代 |
| `range([start,] stop [, step])` | 惰性整数序列 |
| `reversed(seq)` / `sorted(seq)` | 反向 / 排序迭代 |
| `zip(*seqs)` | 并行迭代 |
| `eval(expr)` / `exec(stmt)` | 执行字符串（慎用） |
| `import module [as alias]` | 导入模块 |
| `from module import name` | 导入名称 |

```python
from math import sin as s, pi
print(s(pi / 2))

r = range(1, 1000)
print(type(r), len(r))  # range 对象，不占满内存
```

## 解包与赋值

```python
x, y, z = 1, 2, 3
x, y = y, x                    # 交换
x, y, *rest = 1, 2, 3, 4, 5   # 星号收集剩余项
first, *middle, last = "Albus Percival Wulfric".split()

x = 2
x += 1; x *= 2                 # 增强赋值，就地修改
```

## 条件与循环

**假值**：`False`、`None`、`0`、`""`、`()`、`[]`、`{}`

**比较**：`==` 比较值；`is` 比较对象身份（仅用于 `None` 等单例）；支持 `1 < x < 10` 链式比较。

```python
msg = "small" if x < 10 else "large"
assert 0 < age < 10, f"invalid age: {age}"
```

**循环要点**：

- `for` 遍历可迭代对象；`else` 子句仅在未 `break` 时执行
- 迭代中修改容器时迭代 `.copy()` 或构建新容器

```python
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            break
    else:
        print(n, "is prime")

users = {"Hans": "active", "景太郎": "active", "Éléonore": "inactive"}
for user, status in users.copy().items():
    if status == "inactive":
        del users[user]
```

**推导式**（表达式，非语句）：

```python
[x * x for x in range(10) if x % 2 == 0]
{(x, y) for x in range(3) for y in range(2)}
{i: i ** 2 for i in range(5)}
```

## 字符串格式化

### f-string（推荐，Python 3.6+）

```python
name, score = "King", 95.5
print(f"Hello, {name}! Score: {score:.1f}")
print(f"{name=}")                    # 调试写法（3.8+）
print(f"{score:.0%}")                  # 百分比
print(f"Today: {date.today():%Y-%m-%d}")  # 需 from datetime import date
```

### str.format()

```python
print("Hello, {}! Score: {:.1f}".format("King", 95.5))
print("{name}: {value}".format(name="x", value=42))
```

### % 格式化（旧式，了解即可）

```python
print("%d\t%d" % (1, 2))
print("%.2f" % (32 / 3.3))
```

| 写法 | 含义 |
|------|------|
| `{:.2f}` | 保留 2 位小数 |
| `{:>10}` / `{:0>5}` | 对齐 / 零填充 |
| `{:,}` / `{:.2%}` | 千位分隔 / 百分比 |

## pass、del、exec、eval

| 语句 | 说明 |
|------|------|
| `pass` | 空操作占位符 |
| `del` | 删除变量名或容器元素 |
| `exec()` | 执行语句，无返回值 |
| `eval()` | 求值表达式 |

```python
scope = {"x": 2, "y": 3}
print(eval("x ** y", scope))  # 8
```

> 不要对不可信输入使用 `eval()` / `exec()`。

## match 语句

Python 3.10+ 结构模式匹配：

```python
def http_error(status):
    match status:
        case 400: return "Bad request"
        case 404: return "Not found"
        case 401 | 403: return "Not allowed"
        case _: return "Unknown error"

class Point:
    __match_args__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

match Point(0, 3):
    case Point(x=0, y=y): print(f"Y-axis, y={y}")
    case Point(x=x, y=0): print(f"X-axis, x={x}")
    case Point(): print("Elsewhere")
```

## 最佳实践

1. **字符串插值优先 f-string**；遗留代码外的 `%` 格式化可不再使用。
2. **`print` 用于调试**，正式输出用 `logging`。
3. **迭代时修改字典/集合**用 `.copy()` 或新建容器。
4. **`is` 仅比较身份**（如 `x is None`），值比较用 `==`。
5. **循环 `else`** 适合"搜索未果"场景，比布尔标志更 Pythonic。
6. **不要用 `eval`/`exec` 处理用户输入**。
