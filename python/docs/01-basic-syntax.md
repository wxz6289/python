# Python 基础语法

## 目录

- [基本语法与注释](#基本语法与注释)
  - [程序入口与编码声明](#程序入口与编码声明)
  - [注释](#注释)
  - [语句与换行](#语句与换行)
  - [最佳实践](#最佳实践)
- [变量与赋值](#变量与赋值)
  - [变量命名规范](#变量命名规范)
  - [赋值与多重赋值](#赋值与多重赋值)
  - [删除变量](#删除变量)
  - [交互模式下的 `_`](#交互模式下的-_)
  - [最佳实践](#最佳实践-1)
- [数据类型与转换](#数据类型与转换)
  - [动态类型](#动态类型)
  - [查看类型：`type()`](#查看类型type)
  - [类型转换](#类型转换)
  - [最佳实践](#最佳实践-2)
- [数值类型](#数值类型)
  - [整数与浮点数](#整数与浮点数)
  - [算术运算符](#算术运算符)
  - [复数](#复数)
  - [Decimal 与 Fraction](#decimal-与-fraction)
  - [最佳实践](#最佳实践-3)
- [字符串操作与格式化](#字符串操作与格式化)
  - [创建字符串](#创建字符串)
  - [索引与切片](#索引与切片)
  - [拼接与重复](#拼接与重复)
  - [转义序列与原始字符串](#转义序列与原始字符串)
  - [多行字符串](#多行字符串)
  - [编码与字节类型](#编码与字节类型)
  - [常用字符串方法](#常用字符串方法)
  - [字符串格式化](#字符串格式化)
  - [最佳实践](#最佳实践-4)

---

## 基本语法与注释

### 程序入口与编码声明

在 Unix/Linux/macOS 上，可在脚本首行添加 shebang，指定解释器：

```bash
#!/usr/bin/env python3
```

Python 3 默认使用 UTF-8 编码源文件，通常无需额外声明编码。可通过 `python --help-env` 查看与环境变量相关的帮助信息。

### 注释

Python 支持两种常见注释形式：

| 类型 | 语法 | 用途 |
|------|------|------|
| 单行注释 | `#` | 解释代码逻辑 |
| 文档字符串 | `"""..."""` 或 `'''...'''` | 模块、类、函数的说明文档 |

```python
# 单行注释示例
text = "#comment"  # 行尾注释
print(text)

def greet(name):
    """返回问候语（文档字符串）。"""
    return f"Hello, {name}"
```

### 语句与换行

- **折行**：使用反斜杠 `\` 可在行尾续写；若折行处位于括号 `()`、`[]`、`{}` 内，通常无需 `\`。
- **同行多语句**：使用分号 `;` 分隔，但日常编码中应尽量避免。

```python
import sys

# 括号内自然折行
sys.stdout.write("Hello Python" "\n")
print(
    "hi",
)

# 分号分隔（不推荐频繁使用）
x = 1; y = 2
```

### 最佳实践

- 优先使用 `#` 注释解释**为什么**这样做，而非重复代码字面含义。
- 文档字符串遵循 PEP 257：用简洁语句描述对象用途，必要时补充参数与返回值说明。
- 一行只做一件事；需要分号或 `\` 续行时，优先考虑重构为更清晰的结构。

---

## 变量与赋值

### 变量命名规范

使用变量前必须先赋值（定义）。命名规则如下：

- 由字母、数字、下划线组成，**不能以数字开头**
- 支持 Unicode 字符（如 `变量名 = 1`）
- **区分大小写**（`name` 与 `Name` 是不同变量）
- 不能使用 Python **关键字**或遮蔽内置名称
- 推荐 **蛇形命名法**（`user_name`）；类名常用驼峰式（`UserProfile`）

### 赋值与多重赋值

Python 是动态类型语言：同一变量可在不同时刻持有不同类型的值。

```python
x = 1
x = x + 1
y = 2
print(x + y)  # 4

# 多重赋值（元组解包）
x, y = 1, 2
print(x, y)  # 1 2

# 交换两个变量的值
a, b = 25, 54
a, b = b, a
print(a, b)  # 54 25

# 从序列解包
data = ("Dreamer", "China", "Python")
name, country, language = data
```

### 删除变量

使用 `del` 删除变量引用；删除后再次访问会触发 `NameError`。

```python
z = 10
del z
# print(z)  # NameError: name 'z' is not defined
```

### 交互模式下的 `_`

在交互式解释器（含 IPython、Jupyter）中，上一条表达式的值会赋给内置变量 `_`。应将其视为只读结果缓存，**不要显式赋值给 `_`**，否则会创建同名局部变量并遮蔽内置行为。

### 最佳实践

- 变量名应表意明确：`temp` 不如 `celsius`。
- 用多重赋值简化交换与解包，避免临时变量。
- 不要用单字母 `l`、`O` 等易与 `1`、`0` 混淆的名称。
- 模块级常量可用全大写蛇形命名：`MAX_RETRY = 3`。

---

## 数据类型与转换

### 动态类型

Python 中**变量**没有固定类型，**值**才有类型。赋值操作将名称绑定到对象，而非在固定大小的内存槽中存放数据。

```python
value = 42
value = "forty-two"  # 合法：重新绑定到新的字符串对象
```

### 查看类型：`type()`

`type(obj)` 返回对象的类型：

```python
print(type(2))       # <class 'int'>
print(type(2.3))     # <class 'float'>
print(type(""))      # <class 'str'>
print(type(True))    # <class 'bool'>
```

### 类型转换

常用内置转换函数：

| 函数                  | 作用    |
| ------------------- | ----- |
| `int(x, base=10)`   | 转为整数  |
| `float(x)`          | 转为浮点数 |
| `str(x)`            | 转为字符串 |
| `bool(x)`           | 转为布尔值 |
| complex(real, imag) | 创建复数  |

```python
print(int("231"))      # 231
print(float("23.12"))  # 23.12
print(str(32.21))      # '32.21'

# 字符串与数值不能直接用 + 拼接，需先转换
x = 123
print(str(x) + " items")
```

`int()` 和 `float()` 在无法解析输入时会抛出 `ValueError`；生产代码中应捕获异常或先做校验。

### 最佳实践

- 需要明确类型时，用 `type()` 调试，但业务逻辑中更推荐 `isinstance(obj, int)`（支持继承关系）。
- 用户输入和外部数据一律视为字符串，显式转换后再参与运算。
- 避免依赖隐式类型转换；`"3" + 3` 会报错，应写 `int("3") + 3`。

---

## 数值类型

### 整数与浮点数

Python 内置数值类型包括 `int`、`float`，以及下文介绍的 `complex`、`Decimal`、`Fraction`。

- **int**：任意精度整数，仅受可用内存限制。
- **float**：双精度浮点数，遵循 IEEE 754。

混合类型运算时，整数会被提升为浮点数：

```python
x = 4 * 3.75 - 2
print(x, type(x))  # 13.0 <class 'float'>
```

### 算术运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `+` `-` `*` | 加、减、乘 | `3 + 2` → `5` |
| `/` | 真除法（结果为 float） | `6 / 2` → `3.0` |
| `//` | 地板除（向下取整） | `7 // 2` → `3` |
| `%` | 取余 | `7 % 2` → `1` |
| `**` | 幂运算 | `2 ** 10` → `1024` |

```python
print(6 / 2)   # 3.0
print(6 // 2)  # 3
print(6 % 2)   # 0
print(2 ** 8)  # 256
```

### 复数

虚数单位写作 `j` 或 `J`：

```python
a = 2 + 5j
b = 3 + 2j
c = a * b
print(c, type(c))  # (-4+19j) <class 'complex'>
```

### Decimal 与 Fraction

对精度敏感的场景，避免直接用 `float`：

```python
from decimal import Decimal
from fractions import Fraction

# Decimal：适合货币、精确小数运算
d = Decimal("3.14159")
print(d + Decimal("0.00001"))

# Fraction：适合有理数精确表示
f1 = Fraction(1, 3)
f2 = Fraction(2, 5)
print(f1 + f2)  # 11/15
```

> **注意**：`Decimal` 应从字符串构造（`Decimal('0.1')`），用浮点字面量构造会继承浮点误差。

### 最佳实践

- 比较浮点数用 `math.isclose()`，不要直接 `==`。
- 金额计算用 `Decimal`；比例、分数运算用 `Fraction`。
- 地板除 `//` 与取余 `%` 满足：`a == (a // b) * b + (a % b)`（`b != 0`）。
- 大整数运算无需担心溢出，但应注意时间与空间开销。

---

## 字符串操作与格式化

字符串（`str`）是**不可变**序列，创建后不能就地修改某个位置的字符。

### 创建字符串

可用单引号、双引号或三引号创建：

```python
s1 = 'hello'
s2 = "hello"
s3 = """多行
字符串"""

print(type(s1), len(s1))  # <class 'str'> 5
```

相邻的字符串字面量会自动拼接（**仅适用于字面量**，变量之间无效）：

```python
s = "hello" " world"
print(s)  # hello world

x, y = "Hi! ", "boy and girl."
z = x + y  # 变量之间用 + 拼接
print(z)
```

### 索引与切片

- **索引**：`s[i]` 获取单个字符；支持负索引（`-1` 为最后一个字符）。
- **切片**：`s[start:stop:step]` 获取子串；**包含 `start`，不包含 `stop`**。

切片默认值：

| 参数 | 默认值 |
|------|--------|
| `start` | `0` |
| `stop` | 序列长度 |
| `step` | `1` |

```python
s = "python"
print(s[0])     # p
print(s[-1])    # n
print(s[2:])    # thon
print(s[:3])    # pyt
print(s[2:5])   # tho
print(s[::2])   # pto
print(s[::-1])  # nohtyp（反转）

# 索引越界报错；切片自动截断，不报错
print(s[3:100])  # hon
# s[100]         # IndexError
```

字符串不可变，不能对索引或切片赋值：

```python
# s[0] = 'P'    # TypeError
# s[1:3] = 'ab' # TypeError
```

### 拼接与重复

```python
s1 = "hello"
s2 = "world"
print(s1 + s2)       # helloworld
print(s1 + s2 * 2)   # helloworldworld
print("-" * 20)    # --------------------
```

成员检测：

```python
permission = "rw"
print("w" in permission)      # True
print("x" not in permission)  # True
```

### 转义序列与原始字符串

常见转义序列：

| 序列 | 含义 |
|------|------|
| `\n` | 换行 |
| `\t` | 制表符 |
| `\\` | 反斜杠 |
| `\'` `\"` | 引号 |

在字符串前加 `r` 或 `R` 得到**原始字符串**，反斜杠按字面量处理：

```python
print("hello\nworld")
print(r"hello\nworld")  # hello\nworld

path = "C:\\nowhere\\js"
print(path)
print(r"C:\nowhere\js")
```

原始字符串**不能以奇数个 `\` 结尾**（会与引号转义冲突）。

`repr()` 返回适合开发者阅读的表示形式；`str()` 返回适合终端用户的文本：

```python
print(str("hello\nworld!"))
print(repr("hello\nworld!"))  # 'hello\nworld!'
```

Unicode 转义：

```python
print("\u00C6")           # Æ
print("\U0001f60A")       # 😊
print("This is cat: \N{Cat}")  # This is cat: 🐈
```

### 多行字符串

三引号字符串保留换行；行尾 `\` 可续行并省略换行符：

```python
s = """\
Usage: thingy [OPTIONS]
     -h    Display this usage message
     -H    Hostname to connect to
"""
print(s)
```

### 编码与字节类型

- `str`：Unicode 文本
- `bytes`：不可变字节序列
- `bytearray`：可变字节序列
- memoryview:  内存视图对象 直接访问二进制数据，无需复制

```python
# 编码：str → bytes
b = "hello world".encode("utf-8")
print(b, type(b))

# 解码：bytes → str
text = b.decode("utf-8")
print(text)

# bytearray 支持就地修改
buf = bytearray(b"hello!")
buf[1] = ord("a")
print(buf)  # bytearray(b'hallo!')
```

### 常用字符串方法

**大小写与判断**

```python
s = "we are family, We live in the world"
print(s.lower(), s.upper(), s.title())
print(s.startswith("we"), s.endswith("world"))
print("23".isdigit(), "abc".isalpha())
```

**查找与计数**

```python
title = "$$$ is $$$$ has $$$$ end"
print(title.find("$$$"))       # 0；未找到返回 -1
print(title.index("is"))       # 4；未找到抛 ValueError
print(title.count("$$$"))      # 3
```

**分割与连接**

```python
print("1+2+3".split("+"))           # ['1', '2', '3']
print("/usr/bin/env".split("/"))    # ['', 'usr', 'bin', 'env']
print("a b  c".split())             # 按任意空白分割
print("*".join(["1", "2", "3"]))    # 1*2*3
```

**替换、去除空白与对齐**

```python
print("  hello  ".strip())
print("***hello***".strip("*"))
print("hi".replace("i", "a"))
print("Hello".center(10, "-"))
print("42".zfill(5))  # 0042
```

**字符映射**

```python
table = str.maketrans("ae", "AE")
print("hello".translate(table))  # hEllo
```

`string` 模块提供常用字符集常量：

```python
import string

print(string.digits)        # 0123456789
print(string.ascii_letters)
print(string.punctuation)
```

### 字符串格式化

Python 提供多种格式化方式，推荐优先级：**f-string > `str.format()` > `%` 格式化**。

**f-string（Python 3.6+，首选）**

```python
name, age = "Dreamer", 20
print(f"name: {name}, age: {age}")
print(f"next year: {age + 1}")

from math import pi
print(f"Pi is {pi:.6f}")
```

**`str.format()` 方法**

```python
print("{}, {} and {}".format("Dreamer", "King", "Jeff"))
print("{1}, {0} and {1}".format("Dreamer", "King"))
print("{name} is {value:.2f}".format(name="PI", value=pi))

# 转义花括号
print("{{name}}".format(name="King"))  # {name}
```

**`%` 格式化（旧式，维护遗留代码时可能遇到）**

```python
value = ("Dreamer", 23)
show_str = "My name is %s, I'm %d years old"
print(show_str % value)
```

**`string.Template`（适合用户自定义模板）**

```python
from string import Template

temp = Template("My name is $name, I'm $age years old")
print(temp.substitute(name="Dreamer", age=23))
```

格式化占位符速查：

| 写法 | 说明 |
|------|------|
| `{:.2f}` | 保留两位小数 |
| `{:>10}` | 右对齐，宽度 10 |
| `{:0>5}` | 用 0 填充至宽度 5 |
| `{:,}` | 千位分隔符 |

### 最佳实践

- 日常字符串拼接优先用 f-string，可读性最好。
- 处理文件路径用 `pathlib.Path`，避免手动拼接 `\` 或 `/`。
- 用户输入的文本默认不可信：比较前考虑 `casefold()` 做大小写无关匹配。
- 查找子串：`find()` 返回 `-1` 更安全；确定存在时用 `index()`。
- 需要精确文本处理（货币、编号）时，在格式化阶段控制宽度与小数位，而非事后 `strip()` 修补。
- 字节与文本边界清晰：网络/文件读取得到 `bytes`，尽早 `.decode()` 为 `str` 再处理。

---

*本文档涵盖 Python 基础语法中的注释、变量、类型、数值与字符串。列表、元组、字典、集合及面向对象等主题请参阅同系列其他文档。*
