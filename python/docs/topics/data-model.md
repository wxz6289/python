# Python 数据模型

Python 通过**特殊方法**（dunder methods，如 `__len__`、`__getitem__`）定义对象行为。这些方法由解释器隐式调用，开发者通常实现它们而非直接调用。

> 序列切片语法见 [09-data-structures.md](09-data-structures.md#序列与切片)；排序见 [sorting.md](sorting.md)。

## 目录

- [特殊方法与内置函数](#特殊方法与内置函数)
- [组合优于继承](#组合优于继承)
- [Vector 示例](#vector-示例)
- [抽象基类](#抽象基类)
- [序列模式匹配](#序列模式匹配)
- [序列陷阱](#序列陷阱)
- [array 模块](#array-模块)
- [最佳实践](#最佳实践)

## 特殊方法与内置函数

| 特殊方法 | 触发场景 |
|----------|----------|
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[key]`、切片 |
| `__iter__` | `for x in obj` |
| `__contains__` | `x in obj` |
| `__add__` | `a + b` |
| `__repr__` / `__str__` | `repr()` / `str()` |
| `__init__` | 实例化 |

> 需要调用特殊方法时，优先使用对应内置函数（如 `len(x)` 而非 `x.__len__()`）。

## 组合优于继承

通过实现少量特殊方法，即可让自定义类表现得像内置序列：

```python
import collections
from random import choice

Card = collections.namedtuple("Card", ["rank", "suit"])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list("JQKA")
    suits = "spades diamonds clubs hearts".split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]


deck = FrenchDeck()
print(len(deck), choice(deck), deck[:3])
print(Card("7", "hearts") in deck)
```

## Vector 示例

模拟数值类型，演示运算符重载：

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)


v1 = Vector(2, 4)
v2 = Vector(2, 1)
print(v1 + v2, v1 * 3)
```

## 抽象基类

`collections.abc` 定义序列、映射、可迭代等接口：

```python
from collections import abc, deque


class Stack(abc.MutableSequence):
    def __init__(self):
        self._items = deque()

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __setitem__(self, index, value):
        self._items[index] = value

    def __delitem__(self, index):
        del self._items[index]

    def insert(self, index, value):
        self._items.insert(index, value)

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()
```

## 序列模式匹配

Python 3.10+ `match` 支持序列解构：

```python
def describe(point):
    match point:
        case []:
            return "empty"
        case [x]:
            return f"single {x}"
        case [x, y]:
            return f"pair {x}, {y}"
        case [x, *rest]:
            return f"first {x}, rest {rest}"
```

- `_` 匹配任意一项但不绑定；`*_` 匹配任意数量

## 序列陷阱

### 嵌套列表的浅复制

```python
# 错误：三行共享同一内层列表
board = 3 * [["_"] * 3]
board[1][2] = "X"
print(board)  # 三行都被改了

# 正确：每行独立列表
board2 = [["_"] * 3 for _ in range(3)]
board2[1][2] = "X"
print(board2)
```

### 增量赋值

`+=` 优先调用 `__iadd__`，未实现则回退到 `__add__` 并重新绑定：

```python
lst = [1, 2, 3]
print(id(lst))
lst *= 2
print(id(lst))  # 同一对象（就地扩展）

t = (1, 2, 3)
print(id(t))
t *= 2
print(id(t))  # 不同对象（创建新元组）
```

## array 模块

`array.array` 存储同质数值，比列表更紧凑，支持 `.tofile()` / `.fromfile()` 快速 I/O：

```python
from array import array
from random import random

floats = array("d", (random() for _ in range(100)))
with open("floats.bin", "wb") as fp:
    floats.tofile(fp)

floats2 = array("d")
with open("floats.bin", "rb") as fp:
    floats2.fromfile(fp, 100)
print(floats2[-1])
```

## 最佳实践

1. **实现 `__repr__`**，调试时能看到有用信息。
2. **组合特殊方法**让类融入 Python 生态（可迭代、可切片、可比较）。
3. **就地修改的方法返回 `None`**（如 `list.sort`），避免调用方误以为返回新对象。
4. **不要用 `3 * [[]]` 创建二维列表**，用列表推导。
5. **需要接口契约时用 `collections.abc`** 或 `typing.Protocol`。
6. **增量赋值不是原子操作**，并发场景需注意。
