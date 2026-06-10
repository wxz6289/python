# Python 控制流与语句

本文整理条件分支、循环、模式匹配及相关语句的语法与常见用法。

## 目录

1. [条件语句 if / elif / else](#条件语句-if--elif--else)
2. [while 循环](#while-循环)
3. [for 循环](#for-循环)
4. [range()](#range)
5. [enumerate()](#enumerate)
6. [break 与 continue](#break-与-continue)
7. [for-else](#for-else)
8. [pass 语句](#pass-语句)
9. [迭代时修改集合](#迭代时修改集合)
10. [match / case 模式匹配](#match--case-模式匹配)
11. [del 语句](#del-语句)
12. [weakref 基础](#weakref-基础)

---

## 条件语句 if / elif / else

`if` 根据布尔表达式选择执行路径；`elif` 追加分支；`else` 处理所有条件都不满足的情况。

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"
```

### 最佳实践

- 条件应返回明确布尔值，避免 `if x == True` 等冗余写法。
- 分支多且基于单一变量取值时，优先考虑 `match/case` 或字典分发。
- 嵌套超过两层时，提取函数或提前 `return`，减少缩进。

---

## while 循环

`while` 在条件为真时重复执行，适合次数不确定的场景。

```python
n = 10
while n > 0:
    print(n, end=" ")
    n -= 1
# 10 9 8 7 6 5 4 3 2 1
```

循环变量必须在体内向终止条件靠近，避免死循环。

---

## for 循环

`for` 遍历任意可迭代对象，是 Python 中最常用的循环形式。

```python
for fruit in ["apple", "banana", "cherry"]:
    print(fruit)

for key, value in {"name": "Alice", "age": 30}.items():
    print(f"{key}: {value}")
```

### 最佳实践

- 需要索引时用 `enumerate()`，而非 `range(len(seq))`。
- 不需要索引时直接 `for item in seq`。

---

## range()

`range([start,] stop [, step])` 生成惰性整数序列，常用于计数循环。

```python
for i in range(6):          # 0~5
    print(i, end=" ")
for i in range(3, 6):       # 3~5
    print(i, end=" ")
for i in range(10, 3, -2):  # 10 8 6 4
    print(i, end=" ")

print(sum(range(10)))       # 45
print(range(0, 10))         # range(0, 10) 惰性对象
```

---

## enumerate()

`enumerate(iterable, start=0)` 同时产出索引和元素。

```python
words = ["Mary", "had", "a", "little", "lamb"]
for i, word in enumerate(words):
    print(i, word)

for _, word in enumerate(words):  # 忽略索引
    print(word)
```

---

## break 与 continue

- `break`：立即退出最内层循环。
- `continue`：跳过本次迭代剩余代码，进入下一次。

```python
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print(f"{n} = {x} × {n // x}")
            break

for num in range(2, 10):
    if num % 2 == 0:
        continue
    print(f"奇数: {num}")
```

---

## for-else

`for` 可带 `else`：**仅当循环正常结束**（未被 `break` 打断）时执行 `else`。

```python
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print(f"{n} = {x} × {n // x}")
            break
    else:
        print(f"{n} 是素数")
```

```python
def primes(n):
    for num in range(2, n):
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                break
        else:
            yield num

print(list(primes(25)))  # [2, 3, 5, 7, 11, 13, 17, 19, 23]
```

> `while-else` 语义相同：被 `break` 退出时不执行 `else`。

### 最佳实践

- `for-else` 语义不直观，复杂逻辑优先用标志变量或提取函数。
- 典型场景：搜索"找不到则……"。

---

## pass 语句

`pass` 是空操作占位符，语法上需要语句块但逻辑暂无实现时使用。

```python
class Empty:
    pass

def todo():
    pass  # 待实现
```

---

## 迭代时修改集合

不要在遍历集合的同时直接增删元素，否则可能跳过元素或抛出 `RuntimeError`。

```python
users = {"Hans": "active", "Éléonore": "inactive", "景太郎": "active"}

# 策略一：遍历副本后删除
for user, status in users.copy().items():
    if status == "inactive":
        del users[user]

# 策略二：构建新集合（推荐）
active = {u: s for u, s in users.items() if s == "active"}
```

### 最佳实践

- 删除：遍历 `.copy()` 或先收集待删键再统一删除。
- 过滤：用推导式生成新集合，保留原数据不变。

---

## match / case 模式匹配

Python 3.10+ 引入，按**结构**而非仅按值分支匹配。

### 基本语法

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def where_is(point):
    match point:
        case Point(x=0, y=0):
            print("原点")
        case Point(x=0, y=y):
            print(f"Y 轴, y={y}")
        case Point(x=x, y=0):
            print(f"X 轴, x={x}")
        case Point():
            print("平面上其他位置")
        case _:
            print("不是 Point")
```

### 模式要点

| 特性 | 说明 |
|------|------|
| `_` | 通配符，匹配但不绑定 |
| `*_` | 匹配剩余多项 |
| `\|` | 或模式，如 `case 1 \| 2` |
| `__match_args__` | 类属性，声明位置模式对应的属性名 |
| 守卫 | `case Point(x, y) if x == y:` |
| 序列 | `[x, y, *rest]` 匹配列表/元组（不含迭代器/字符串） |
| 映射 | `{"key": val}` 额外键被忽略 |
| 字面值 | `True`/`False`/`None` 按 `is` 比较 |

`__match_args__` 与守卫示例：

```python
class Point:
    __match_args__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

match (Point(0, 1), Point(0, 3)):
    case [Point(0, y1), Point(0, y2)]:
        print(f"两点在 Y 轴: {y1}, {y2}")

match Point(2, 2):
    case Point(x, y) if x == y:
        print(f"对角线 x=y={x}")
```

枚举匹配：

```python
from enum import Enum

class Color(Enum):
    RED, GREEN, BLUE = "red", "green", "blue"

match Color.GREEN:
    case Color.RED:   print("红")
    case Color.GREEN: print("绿")
    case Color.BLUE:  print("蓝")
```

### 最佳实践

- 简单值比较用 `if/elif`；结构化解构、多类型分发用 `match`。
- 始终保留 `case _:` 兜底。
- 模式变量会泄漏到 `match` 块作用域，注意命名冲突。

---

## del 语句

`del` 删除**名称绑定**，而非直接销毁对象。所有引用消失后对象才被回收。

```python
a = [1, 2, 3]
b = a
del a          # 删除名称 a，列表仍被 b 引用
del b          # 最后一个引用消失，对象可回收

items = [10, 20, 30]
del items[1]   # 删除元素
```

CPython 以**引用计数**为主；2.0 起增加**分代垃圾回收**处理循环引用。

### 最佳实践

- `del` 不能替代良好作用域管理；函数结束局部变量自动回收。
- 循环引用场景可显式 `del` 大对象或改用 `weakref`。

---

## weakref 基础

`weakref` 提供**弱引用**：不增加引用计数，对象回收后弱引用自动失效。

```python
import weakref

class MyClass:
    pass

obj = MyClass()
ref = weakref.ref(obj)
print(ref() is obj)  # True
del obj
print(ref())         # None
```

`weakref.finalize` 在对象即将被回收时执行清理回调：

```python
import weakref

s1 = {1, 2, 3}
s2 = s1

def on_finalize():
    print("集合已被回收")

ender = weakref.finalize(s1, on_finalize)
del s1                # s2 仍引用，回调不触发
s2 = "spam"           # 原集合无引用，触发 finalize
print(ender.alive)    # False
```

部分不可变类型"复制"时返回同一对象：

```python
print((1, 2, 3) is tuple((1, 2, 3)))       # True
print("hello" is "hello")                   # True（驻留）
print(frozenset({1,2}) is frozenset.copy(frozenset({1,2})))  # True
```

### 最佳实践

- 缓存、观察者模式用 `WeakValueDictionary` 避免内存泄漏。
- 资源清理优先用 `with` 或 `try/finally`；`finalize` 作补充。
- `int`、`str`、`tuple` 等部分内置类型不支持直接弱引用。
