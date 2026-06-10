# Python 数据结构

本文整理 Python 内置数据结构——序列、列表、元组、字典与集合，并讲解引用语义、浅拷贝/深拷贝，以及可变默认参数陷阱。

## 目录

- [序列与切片](#序列与切片)
- [列表](#列表)
- [元组与 namedtuple](#元组与-namedtuple)
- [字典](#字典)
- [集合](#集合)
- [引用与复制（浅拷贝 / 深拷贝）](#引用与复制浅拷贝--深拷贝)
- [可变默认参数陷阱](#可变默认参数陷阱)

---

## 序列与切片

**序列（sequence）** 是按顺序排列的元素集合，包括 `str`、`list`、`tuple`、`bytes`、`bytearray` 等。

### 通用操作

| 操作 | 说明 |
|------|------|
| `len(seq)` | 返回元素个数 |
| `seq[i]` | 索引；正向 `0`~`n-1`，负向 `-n`~`-1` |
| `seq[start:stop:step]` | 切片，返回新序列 |
| `+`、`*` | 拼接与重复 |
| `in` / `not in` | 成员检测 |

```python
s = "python is good"
print(len(s), s[0], s[-1])   # 14 p d
print("good" in s)           # True
print(s + "!", "ha" * 3)     # python is good! hahaha
```

### 切片语法

格式 `[start:stop:step]`，三者均可省略：

| 参数 | 省略时的默认值 | 说明 |
|------|---------------|------|
| `start` | `0` | 起始索引（包含） |
| `stop` | 序列长度 | 结束索引（**不包含**） |
| `step` | `1` | 步长；为 `0` 报错 |

> 索引越界报错，切片自动处理越界。结果**包含** `start`，**不包含** `stop`。

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(numbers[2:6])      # [2, 3, 4, 5]
print(numbers[6:6])      # []
print(numbers[3:-2])     # [3, 4, 5, 6, 7]
print(numbers[:-2])      # [0, 1, 2, 3, 4, 5, 6, 7]
print(numbers[5:])       # [5, 6, 7, 8, 9]   从索引 5 到末尾
print(numbers[-3:])      # [7, 8, 9]         最后 3 个
print(numbers[-3:0])     # []  负 start > stop 时为空
```

`step` 为负时从右向左取，`start` 应大于 `stop`：

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

print(numbers[1:10:2])   # [1, 3, 5, 7, 9]
print(numbers[::4])      # [0, 4, 8]
print(numbers[8:3:-2])   # [8, 6, 4]
print(numbers[3:8:-2])   # []
print(numbers[8::-3])    # [8, 5, 2]

s = "python is good"
print(s[12:2:-2])        # 'do s'

tag = "https://juejin.cn/post/6844904068888920071"
print(tag[8:17])         # juejin.cn
```

### 最佳实践

- 切片默认：`start=0`、`stop=长度`、`step=1`（原 notebook 误写 `start=1`，已修正）。
- `seq[:]` 或 `list(seq)` 仅对一维结构有效；嵌套对象仍共享引用。
- 负步长切片先想清楚方向再写索引。

---

## 列表

**列表（list）** 用 `[]` 表示，**可变**、**有序**，元素可不同类型（实践中通常同质）。

```python
l = list("hello")
print(l, "".join(l))     # ['h','e','l','l','o'] hello

x = [1, 2, 3]
x[1] = 4
print(x)                 # [1, 4, 3]
```

### 切片赋值

切片赋值可改变列表大小，甚至清空：

```python
name = list("Perl")
name[2:] = list("ar")
print(name)              # ['P', 'e', 'a', 'r']

numbers = [1, 5]
numbers[1:1] = [2, 3, 4] # 插入
numbers[1:4] = []        # 删除
numbers[:] = []          # 清空
print(numbers)           # []

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
del numbers[-1:2:-3]     # 删除 9, 6, 3
print(numbers)           # [1, 2, 4, 5, 7, 8]
```

### 常用方法

| 方法 | 说明 |
|------|------|
| `append(x)` | 末尾追加**单个**元素 |
| `extend(iterable)` | 扩展，等价 `+=` |
| `insert(i, x)` | 在索引 `i` 插入 |
| `remove(x)` / `pop([i])` | 删除元素 |
| `index(x)` / `count(x)` | 查找 / 计数 |
| `sort()` / `sorted()` | 原地排序 / 新列表 |
| `clear()` | 清空 |

```python
lst = [1, 2, 3]
lst.append(4)
lst.extend([5, 6])
print(lst)               # [1, 2, 3, 4, 5, 6]

knight = ["we", "are", "the", "knight", "who", "say", "hi"]
print(knight.index("hi"))  # 6

x = [2, 1, 3, 6]
y = sorted(x)            # x 不变
print(y, x)              # [1, 2, 3, 6] [2, 1, 3, 6]
```

### 拼接与嵌套

```python
l1, l2 = [1, 2, 3], ["Hello", "Hi", "Goodbye"]
l3 = l1 + l2             # 拼接，不修改 l1
l4 = [l1, l2]            # 嵌套
print(l4[1][1], l4[0][1:])  # Hi [2, 3]

print([23] * 3, [None] * 5)
```

### 最佳实践

- `append` 追加单个元素；多个元素用 `extend`，避免嵌套列表。
- `a + b` 创建新列表；`a.extend(b)` / `a += b` 原地修改。
- 排序：保留原列表用 `sorted()`，允许原地修改用 `.sort()`。
- 勿用 `[[0]*3]*3` 建矩阵，各行共享引用。
- 遍历时删除元素应迭代副本：`for item in lst.copy():`。

---

## 元组与 namedtuple

**元组（tuple）** 用 `()` 表示（可省略），**不可变**、**有序**，不能增删改元素。

### 创建与操作

```python
t1 = (1, 2, 3, 2)
print(type(t1), t1.count(2))  # tuple 2

t2 = (2,)                # 单元素元组末尾必须有逗号
print(type(t2), type((2)))    # tuple int

t3 = 1, 2, 3,            # 括号可省略
print(t3, (3 + 4,))      # (1, 2, 3) (7,)

t = (1, 2, 3)
print(t[1:], t * 2)       # (2, 3) (1, 2, 3, 1, 2, 3)
# t[0] = 6  # TypeError
```

### 解包

```python
a, b = 25, 54
a, b = b, a              # 交换
print(a, b)              # 54 25

name, country, lang = ("Dreamer", "China", "Python")
print(name, country, lang)
```

### 元组中的可变元素

元组不可变，但元素若为可变对象，其内容仍可修改：

```python
t1 = 1, 2, [30, 40]
t2 = 1, 2, [30, 40]
print(t1 == t2)          # True
print(id(t1[-1]) == id(t2[-1]))  # False

t1[-1].append(50)
print(t1)                # (1, 2, [30, 40, 50])
print(t2)                # (1, 2, [30, 40])
```

### namedtuple

`collections.namedtuple` 创建带命名字段的轻量元组子类：

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y", "z"])
point = Point(1, 2, 3)
print(point.x, point.y, point.z)  # 1 2 3
print(point)                       # Point(x=1, y=2, z=3)
# point.x = 2  # AttributeError
```

### 最佳实践

- 单元素元组写 `(x,)`，不要写 `(x)`。
- 返回固定结构的多值用元组，暗示不可扩展。
- 元组可作字典键（列表不行）。
- 元组内含可变对象会增加理解成本，应谨慎。

---

## 字典

**字典（dict）** 是键值映射，**可变**、**有序**（Python 3.7+ 插入顺序）。键须不可变且可哈希。

### 创建与基本操作

```python
phone_book = {"Alice": "2341", "Beth": "9102", "Cecil": "3528"}
print(phone_book["Alice"])

d = dict([("name", "Gumy"), ("age", 23)])
d = dict(name="king", age=26)
d["age"] = 20
print("name" in d)       # True  in 检测键
del d["name"]
```

### 字典 vs 列表

| 特性 | 列表 | 字典 |
|------|------|------|
| 访问 | 整数索引 | 键 |
| 添加 | `append` 等 | `d[key] = value` |
| `in` | 检测**值** | 检测**键** |

```python
x = []; x.append(2)      # 不能 x[2] = 'king'
y = {}; y[1] = "king"    # 可直接添加新键
```

### 嵌套与安全访问

```python
people = {
    "Alice": {"phone": "2341", "addr": "Foo drive 23"},
    "Beth":  {"phone": "9102", "addr": "Bar street 42"},
    "Cecil": {"phone": "3158", "addr": "Baz avenue 90"},
}
labels = {"phone": "phone number", "addr": "address"}

name, key = "Cecil", "phone"
print(f"{name}'s {labels[key]} is {people[name][key]}")

# 安全访问
person = people.get("king", {})
print(person.get("phone", "not available"))  # not available
```

### 常用方法

| 方法 | 说明 |
|------|------|
| `get(key[, default])` | 安全取值 |
| `setdefault(key[, default])` | 不存在则设置 |
| `keys()` / `values()` / `items()` | 视图 |
| `update()` | 合并更新 |
| `pop()` / `popitem()` / `clear()` | 删除 |
| `copy()` | 浅拷贝 |
| `fromkeys(keys[, value])` | 批量创建 |

```python
d = {"title": "Python Site", "url": "http://python.org", "spam": 0}
print(list(d.items()), list(d.keys()))

d.setdefault("name", "python")
d.update({"title": "Python Web"}, url="http://python.org")
print(d)
```

字典格式化用 `format_map()`：

```python
phone_book = {"Alice": "2341", "Beth": "9102"}
print("Alice's phone is {Alice}.".format_map(phone_book))
```

### 最佳实践

- 取值优先 `d.get(key, default)`，避免 `KeyError`。
- "不存在则创建"用 `setdefault` 或 `collections.defaultdict`。
- 遍历用 `for k, v in d.items()`。
- `d.copy()` 是浅拷贝，嵌套可变值仍共享。

---

## 集合

**集合（set）** 用 `{}` 或 `set()` 创建，**可变**、**无序**、元素**唯一**，不支持索引。

```python
s = {1, 2, 3, 4}
s.add(5)
print(s)                 # {1, 2, 3, 4, 5}

s = set([1, 2, 2, 3])
print(s)                 # {1, 2, 3}
```

### 集合运算

```python
a, b = {1, 2, 3, 4}, {3, 4, 5, 6}
print(a | b)             # 并集
print(a & b)             # 交集 {3, 4}
print(a - b)             # 差集 {1, 2}
print(a ^ b)             # 对称差
print(3 in a)            # True
```

`frozenset` 不可变，可作字典键：`d = {frozenset([1, 2]): "key"}`

### 最佳实践

- 去重：`list(set(lst))` 丢顺序；保序用 `list(dict.fromkeys(lst))`。
- 频繁成员检测时转集合，平均 O(1)。
- 空集合用 `set()`，`{}` 是空字典。
- 元素须可哈希，列表不能入集合。

---

## 引用与复制（浅拷贝 / 深拷贝）

变量是**对象引用**，赋值不复制数据。

### 引用赋值

```python
a = [1, 2, 3]
c = [1, 2, 3]
print(a == c, a is c)    # True False

b = a
b[1:1] = [4, 5, 6]
print(a)                 # [1, 4, 5, 6, 2, 3]
print(a is b)            # True
```

### 浅拷贝

浅拷贝创建新容器，**内层可变对象仍共享**：

```python
l = [[1, 2], 2, 3]
l2 = l.copy()            # 等价 l[:]
l2.append(4)
l2[0][0] = 2
print(l2)                # [[2, 2], 2, 3, 4]
print(l)                 # [[2, 2], 2, 3]  内层共享

l1 = [3, [65, 55, 44], (7, 8, 9)]
l2 = list(l1)
l1[1].remove(55)
l2[1] += [33, 22]
l2[2] += (10, 11)        # 元组 += 产生新对象
print("l1:", l1)         # [3, [65, 44, 33, 22], (7, 8, 9)]
print("l2:", l2)         # [3, [65, 44, 33, 22], (7, 8, 9, 10, 11)]
```

### 深拷贝与 Bus 示例

```python
from copy import copy, deepcopy

class Bus:
    def __init__(self, passengers=None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = list(passengers)

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        self.passengers.remove(name)

bus1 = Bus(["Alice", "Bill", "Claire", "David"])
bus2 = copy(bus1)        # 浅拷贝：passengers 列表共享
bus3 = deepcopy(bus1)    # 深拷贝：完全独立

bus1.drop("David")
print(bus2.passengers)   # ['Alice', 'Bill', 'Claire']
print(bus3.passengers)   # ['Alice', 'Bill', 'Claire', 'David']
print(id(bus1.passengers) == id(bus2.passengers))  # True
print(id(bus1.passengers) == id(bus3.passengers))  # False
```

```python
# 循环引用与字典浅拷贝
a = [10, 20]; b = [a, 30]; a.append(b)
c = deepcopy(a)          # [10, 20, [[...], 30]]

d = {"names": ["Alfred", "Bertrand"]}
c, dc = d.copy(), deepcopy(d)
d["names"].append("Clive")
print(c["names"], dc["names"])
# ['Alfred', 'Bertrand', 'Clive']  ['Alfred', 'Bertrand']
```

### 拷贝方式对比

| 方式 | 新容器 | 内层对象 | 场景 |
|------|--------|----------|------|
| `b = a` | 否 | 共享 | 别名 |
| `a[:]` / `a.copy()` | 是 | 共享 | 一维列表 |
| `copy.copy(a)` | 是 | 共享 | 任意浅拷贝 |
| `copy.deepcopy(a)` | 是 | 独立 | 嵌套可变结构 |

### 最佳实践

- 赋值是引用；修改可变对象影响所有别名。
- 一维用 `lst.copy()`；嵌套用 `deepcopy`。
- 同一对象用 `is`，值相等用 `==`。
- 函数参数传引用，函数内修改可变实参会影响调用方。

---

## 可变默认参数陷阱

默认参数在**定义时只求值一次**，存为 `__defaults__`。可变对象作默认值时，多次调用共享同一对象。

### 问题演示：HuntedBus

```python
class HuntedBus:
    def __init__(self, passengers=[]):   # 危险！
        self.passengers = passengers

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        self.passengers.remove(name)

bus1 = HuntedBus(["Alice", "Bill"])
bus1.pick("Charlie")
bus1.drop("Alice")
print(bus1.passengers)   # ['Bill', 'Charlie']

bus2 = HuntedBus()
bus2.pick("Carrie")
print(bus2.passengers)   # ['Carrie']

bus3 = HuntedBus()
print(bus3.passengers)   # ['Carrie']  继承了 bus2 的状态！
bus3.pick("Dave")
print(bus2.passengers)   # ['Carrie', 'Dave']
print(bus3.passengers)   # ['Carrie', 'Dave']

print(HuntedBus.__init__.__defaults__)
print(HuntedBus.__init__.__defaults__[0] is bus2.passengers)  # True
```

### 正确写法：Bus

```python
class Bus:
    def __init__(self, passengers=None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = list(passengers)

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        self.passengers.remove(name)

bus1 = Bus(["Alice", "Bill", "Claire", "David"])
bus2 = Bus()
bus2.pick("Eve")
print(bus1.passengers)   # ['Alice', 'Bill', 'Claire', 'David']
print(bus2.passengers)   # ['Eve']
```

### 函数默认参数

```python
# 错误
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))       # [1]
print(add_item(2))       # [1, 2]  不是 [2]！

# 正确
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

print(add_item(1))       # [1]
print(add_item(2))       # [2]
```

### 最佳实践

- **永远不要**用 `[]`、`{}`、`set()` 作默认参数。
- 惯用：`def func(arg=None): if arg is None: arg = []`。
- 复制调用方传入的可变参数：`list(arg)` 或 `copy.copy(arg)`。
- `dataclass` 中用 `field(default_factory=list)`，不用 `default=[]`。

掌握引用语义——赋值传引用、浅拷贝只复制外层、深拷贝完全隔离、可变默认参数在定义时共享——是写出安全可预测 Python 代码的基础。
