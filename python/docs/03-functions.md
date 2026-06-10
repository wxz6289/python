# Python 函数

本文整理函数定义、作用域、参数机制及常见陷阱。

## 目录

1. [定义与调用](#定义与调用)
2. [文档字符串 docstring](#文档字符串-docstring)
3. [作用域与 LEGB 规则](#作用域与-legb-规则)
4. [global 与 nonlocal](#global-与-nonlocal)
5. [参数传递：可变与不可变](#参数传递可变与不可变)
6. [位置参数与关键字参数](#位置参数与关键字参数)
7. [默认参数](#默认参数)
8. [默认参数陷阱](#默认参数陷阱)
9. [*args 与 **kwargs](#args-与-kwargs)
10. [仅位置参数 / 与仅关键字参数 *](#仅位置参数--与仅关键字参数-)
11. [lambda 表达式](#lambda-表达式)
12. [嵌套函数](#嵌套函数)
13. [函数作为一等公民](#函数作为一等公民)

---

## 定义与调用

`def` 定义函数，函数体须缩进；`return` 返回值，无 `return` 则返回 `None`。

```python
def add(a, b, c):
    """返回三数之和。"""
    return a + b + c

print(add(1, 2, 3))
print(add(a=1, b=2, c=3))  # 关键字调用，顺序无关
```

### 最佳实践

- 函数名用蛇形命名，动词开头（`get_`、`calc_`、`is_`）。
- 单一职责，过长则拆分；避免与内置名同名。

---

## 文档字符串 docstring

函数第一个语句可以是三引号文档字符串，通过 `__doc__`、`help()` 访问。

```python
def greet(name):
    """向指定用户打印问候语。"""
    print(f"Hello, {name}!")

print(greet.__doc__)       # 向指定用户打印问候语。
greet("Alice")             # 无 return → 返回 None
```

---

## 作用域与 LEGB 规则

Python 按 **LEGB** 顺序查找名称：

| 层级 | 含义 | 示例 |
|------|------|------|
| **L**ocal | 当前函数 | 函数内赋值 |
| **E**nclosing | 外层嵌套函数 | 闭包自由变量 |
| **G**lobal | 模块全局 | 模块顶层变量 |
| **B**uilt-in | 内置 | `len`、`print` |

```python
x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)       # local
    inner()
    print(x)           # enclosing
outer()
print(x)               # global
```

**读取**外层变量无需声明；**赋值**默认创建局部变量，修改外层须用 `nonlocal`/`global`。

### 最佳实践

- 减少全局变量依赖，通过参数和返回值传递数据。
- 避免与外层同名变量赋值导致意外遮蔽。

---

## global 与 nonlocal

`global` 修改模块级变量；`nonlocal` 修改最近一层外层函数的变量。

```python
count = 0
def increment():
    global count
    count += 1

def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

increment()                # count → 1
c = make_counter()
print(c(), c())            # 1 2
```

模块级变量在函数内**只读**无需 `global`；**赋值**才需要。

### 最佳实践

- 优先用闭包、类或显式参数替代 `global`。
- 嵌套层级过深时用类封装，而非多层 `nonlocal`。

---

## 参数传递：可变与不可变

参数传递是**对象引用的传递**。

- **不可变**（`int`、`str`、`tuple`）：函数内重新赋值不影响外部。
- **可变**（`list`、`dict`、`set`）：原地修改影响外部同一对象。

```python
def rebind(n):
    n = "changed"

name = "original"
rebind(name)
print(name)  # original

def mutate(lst):
    lst[0] = "changed"

names = ["Alice", "Bob"]
mutate(names)
print(names)          # ['changed', 'Bob']
mutate(names[:])      # 传入副本，原列表不变
```

### 最佳实践

- 不希望副作用时传入副本；需要修改时在 docstring 中说明。

---

## 位置参数与关键字参数

- **位置参数**：按定义顺序传入。
- **关键字参数**：`name=value`，顺序无关，须位于所有位置参数之后。

```python
def greet(greeting, name):
    print(f"{greeting}, {name}")

greet("Hello", "Python")
greet(name="Python", greeting="Hi")
greet("Hi", name="C")  # 位置 + 关键字混合
```

不能对同一参数重复赋值；所有关键字名须对应形参。

---

## 默认参数

带默认值的参数可省略；默认值在**函数定义时**求值，只求值一次。

```python
def greet(name, greeting="Hello", punctuation="!"):
    print(f"{greeting}, {name}{punctuation}")

greet("Mars")
greet("Mars", "Howdy")
greet("Mars", punctuation=".")

i = 5
def f(arg=i):
    print(arg)
i = 6
f()  # 5（定义时绑定，不受后续 i=6 影响）
```

---

## 默认参数陷阱

**切勿将可变对象用作默认值**，所有调用共享同一对象。

```python
# 错误
def append_item(item, bucket=[]):
    bucket.append(item)
    return bucket
print(append_item(1))  # [1]
print(append_item(2))  # [1, 2]  ← 意外共享

# 正确
def append_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### 最佳实践

- 默认值用 `None` 占位，函数体内创建新对象。
- 默认参数须位于非默认参数之后。

---

## *args 与 **kwargs

- `*args`：收集多余位置参数为元组。
- `**kwargs`：收集多余关键字参数为字典。

```python
def report(title, *args, **kwargs):
    print(title, args, kwargs)

report("日志", "a", "b", level="INFO")
```

单独 `*` 后的参数必须用关键字传递：

```python
def connect(host, *ports, timeout=30):
    print(host, ports, timeout)

connect("localhost", 8080, timeout=5)
```

形参顺序：位置 → 默认 → `*args` → 仅关键字 → `**kwargs`。

```python
def demo(x, y, z=3, *extra, **opts):
    print(x, y, z, extra, opts)

demo(1, 2, 3, 5, 6, foo=11)
# 1 2 3 (5, 6) {'foo': 11}
```

---

## 仅位置参数 / 与仅关键字参数 *

Python 3.8+ 用 `/` 和 `*` 限制传参方式：

```python
def f(pos1, pos2, /, pos_or_kwd, *, kwd1, kwd2):
    # pos1, pos2  → 仅位置
    # pos_or_kwd  → 位置或关键字
    # kwd1, kwd2  → 仅关键字
    pass
```

```python
def concat(*args, sep="/"):
    return sep.join(args)

print(concat("a", "b", "c"))           # a/b/c
print(concat("a", "b", sep="."))         # a.b

def foo(name, /, **kwds):
    return name, kwds

print(foo(42, extra="x"))  # (42, {'extra': 'x'})
```

### 最佳实践

- 公共 API 中对易混淆参数使用 `/` 和 `*`，调用方式一目了然。

---

## lambda 表达式

`lambda` 创建匿名单行函数，只能含一个表达式。

```python
square = lambda x: x ** 2
add = lambda x, y: x + y
print(square(5), add(2, 6))  # 25 8

pairs = [(1, 2), (2, 0), (4, 1)]
print(sorted(pairs, key=lambda p: p[1]))

adjust = lambda x: x - 1 if x > 5 else x + 1
print(adjust(6), adjust(3))  # 5 4
```

### 最佳实践

- 逻辑复杂时改用 `def`；`lambda` 适合简单回调（排序 key 等）。
- 不要用 `lambda` 产生副作用。

---

## 嵌套函数

函数内可定义内部函数；内层函数可形成**闭包**，捕获外层变量。

```python
def make_multiplier(n):
    def multiply(x):
        return x * n   # 闭包捕获 n
    return multiply

double = make_multiplier(2)
print(double(5))  # 10
```

修改外层变量须用 `nonlocal`；只读则直接引用。

### 最佳实践

- 内层函数仅在外层逻辑需要复用且不宜暴露时使用。

---

## 函数作为一等公民

函数是对象，可赋值、传参、返回；`callable()` 判断是否可调用。

```python
import math

f = max
print(callable(42), callable(math.sqrt))  # False True
print(f(5, 2, 3))                         # 5

def apply(func, x):
    return func(x) + 1

print(apply(math.sqrt, 4))                # 3.0
print(apply(lambda x: x ** x, 3))         # 27
```

### 最佳实践

- 策略模式、回调、装饰器都依赖函数是一等公民。
- 用 `functools.partial` 固定部分参数，替代过度使用 `lambda`。
- 参数校验用类型注解 + 显式异常，而非静默失败。
