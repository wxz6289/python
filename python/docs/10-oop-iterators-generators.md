# 面向对象、迭代器与生成器

类与继承、多态与协议、迭代器与生成器，以及 `yield` 与生成器表达式。

## 目录

1. [类的基础](#类的基础)
2. [继承与方法重写](#继承与方法重写)
3. [super() 与初始化链](#super-与初始化链)
4. [多态与鸭子类型](#多态与鸭子类型)
5. [协议](#协议)
6. [继承内置类型：CounterList](#继承内置类型counterlist)
7. [特性与类方法速览](#特性与类方法速览)
8. [__getattr__ 与属性拦截](#__getattr__-与属性拦截)
9. [迭代器协议](#迭代器协议)
10. [生成器与 yield](#生成器与-yield)
11. [生成器表达式](#生成器表达式)
12. [生成器高级操作](#生成器高级操作)
13. [实战：八皇后](#实战八皇后)
14. [最佳实践](#最佳实践)

---

## 类的基础

Python 3 所有类隐式继承 `object`。`__init__` 初始化实例；`__del__` 在垃圾回收前调用（时机不确定，勿依赖）。

| 特殊方法 | 作用 |
|----------|------|
| `__init__` | 构造/初始化 |
| `__repr__` / `__str__` | 开发者/用户友好的字符串 |
| `__del__` | 析构（不推荐管理资源） |

```python
class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

p = Point(1, 2, 3)
p.x = 2
print(p)   # Point(2, 2, 3)
```

可变默认值陷阱——用 `None` 兜底：

```python
class Bus:
    def __init__(self, passengers=None):
        self.passengers = [] if passengers is None else list(passengers)
```

### 最佳实践

实现 `__repr__`；资源管理用 `with`，不依赖 `__del__`；可变默认参数用 `None`。

---

## 继承与方法重写

子类继承父类属性和方法，可**重写**父类方法并扩展接口。

```python
class Bird:
    def __init__(self):
        self.hungry = True

    def eat(self):
        if self.hungry:
            print("Aaaa...."); self.hungry = False
        else:
            print("No, thanks.")

class SongBird(Bird):
    def __init__(self):
        super().__init__()
        self.sound = "Squawk"

    def sing(self):
        print(self.sound)

s = SongBird()
s.sing(); s.eat()
```

---

## super() 与初始化链

重写 `__init__` 须调用父类构造。`super()` 按 MRO 解析父类方法；多重继承时每个子类只调一次 `super().__init__()`。

```python
class A:
    def __init__(self): print("A")

class B(A):
    def __init__(self):
        super().__init__()
        print("B")

B()   # A → B
```

| 写法 | 说明 |
|------|------|
| `super().__init__()` | Python 3 推荐 |
| `A.__init__(self)` | 硬编码，多重继承易出错 |

---

## 多态与鸭子类型

多态基于**鸭子类型**：不关心类型，只关心行为。

```python
class A:
    def hello(self): print("A")
class B(A):
    def hello(self): print("B")

def greet(obj):
    obj.hello()

greet(B())   # B
greet(A())   # A
```

---

## 协议

**协议**约定对象应实现的方法及语义，无需继承特定基类。

### 序列/映射协议

| 方法 | 说明 |
|------|------|
| `__len__` | 元素个数 |
| `__getitem__` | 按索引/键取值 |
| `__setitem__` / `__delitem__` | 赋值 / 删除（可变对象） |
| `__iter__` | 返回迭代器 |

```python
class ArithmeticSequence:
    def __init__(self, start=0, step=1):
        self.start, self.step = start, step
        self._changed = {}

    def __getitem__(self, key):
        if not isinstance(key, int) or key < 0:
            raise (TypeError if not isinstance(key, int) else IndexError)
        return self._changed.get(key, self.start + key * self.step)

    def __setitem__(self, key, value):
        self._changed[key] = value

seq = ArithmeticSequence(2, 3)
print(seq[3])    # 11
seq[4] = 8; print(seq[4])   # 8
```

---

## 继承内置类型：CounterList

直接继承 `list`、`dict` 等扩展行为，重写时调用 `super()`：

```python
class CounterList(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.counter = 0

    def __getitem__(self, key):
        self.counter += 1
        return super().__getitem__(key)

c = CounterList(range(10))
c.reverse()
total = c[0] + c[2]
print(c.counter)   # 2
```

---

## 特性与类方法速览

详见 [08-properties-descriptors.md](08-properties-descriptors.md)。

```python
class Rectangle:
    def __init__(self):
        self._width = self._height = 0

    @property
    def size(self):
        return self._width, self._height

    @size.setter
    def size(self, v):
        self._width, self._height = v

class MyClass:
    @staticmethod
    def smeth(): print("静态方法")

    @classmethod
    def cmeth(cls): print(f"类方法 cls={cls}")
```

---

## __getattr__ 与属性拦截

| 方法 | 时机 |
|------|------|
| `__getattribute__` | 每次访问 |
| `__getattr__` | 常规查找失败后 |
| `__setattr__` | 每次赋值 |

```python
class Rectangle:
    def __setattr__(self, name, value):
        if name == "size":
            self.__dict__["width"], self.__dict__["height"] = value
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name == "size":
            return self.width, self.height
        raise AttributeError(name)

r = Rectangle()
r.size = (23, 12)
print(r.size)   # (23, 12)
```

**陷阱**：`__setattr__` 中 `self.name = v` 会递归，应写 `self.__dict__[name] = v`。

---

## 迭代器协议

| 概念 | 要求 |
|------|------|
| 可迭代对象 | `__iter__()` 返回迭代器 |
| 迭代器 | `__iter__` 返回 self；`__next__` 返回下一项或抛 `StopIteration` |

```python
class Fibs:
    def __init__(self):
        self.a, self.b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        return self.a

for f in Fibs():
    if f > 100:
        print(f); break   # 144
```

### 最佳实践

大数据集用迭代器逐条处理；迭代器一次性，重复遍历需重新 `iter()`。

---

## 生成器与 yield

含 `yield` 的函数调用后返回生成器对象，惰性产出值。

```python
def flatten(nested):
    for sub in nested:
        for el in sub:
            yield el

print(list(flatten([[1,2],[3,4]])))   # [1,2,3,4]
```

递归展平（字符串视为原子）：

```python
def flatten_deep(nested):
    try:
        try: nested + ""
        except TypeError: pass
        else: raise TypeError
        for sub in nested:
            yield from flatten_deep(sub)
    except TypeError:
        yield nested

print(list(flatten_deep([[2,3], "hi", 4])))
```

---

## 生成器表达式

圆括号语法，惰性求值；单参数时可省略外层括号：

```python
total = sum(x**2 for x in range(4))          # 14
g = ((i+2)**i for i in range(3, 6))
print(next(g), next(g))   # 125 1296
```

| 对比 | 列表推导 | 生成器表达式 |
|------|---------|-------------|
| 求值 | 立即 | 惰性 |
| 内存 | 全部结果 | 常量 |
| 重用 | 可多次 | 一次性 |

---

## 生成器高级操作

| 方法 | 说明 |
|------|------|
| `send(v)` | 向 `yield` 发送值，`yield` 表达式结果为 `v` |
| `throw(exc)` | 在 `yield` 处注入异常 |
| `close()` | 引发 `GeneratorExit`，触发 `finally` 清理 |

---

## 实战：八皇后

```python
def conflict(state, col):
    row = len(state)
    return any(abs(state[i]-col) in (0, row-i) for i in range(row))

def queens(n, state=()):
    for col in range(n):
        if not conflict(state, col):
            if len(state) == n-1:
                yield state + (col,)
            else:
                yield from queens(n, state + (col,))

def show(sol):
    n = len(sol)
    for c in sol:
        print(". "*c + "X " + ". "*(n-c-1))

sol = next(queens(8))
show(sol)
```

---

## 最佳实践

### 面向对象

| 原则 | 说明 |
|------|------|
| 组合优于继承 | HAS-A 代替不必要的 IS-A |
| super() 初始化 | 子类 `__init__` 调用 `super().__init__()` |
| 显式接口 | 协议方法优于 `__getattr__` 魔法 |
| 可变默认值 | `None` 兜底 |

### 迭代与生成

| 原则 | 说明 |
|------|------|
| 大数据 | 生成器 / 生成器表达式 |
| 多次遍历 | 转 `list` 或重新创建生成器 |
| itertools | 标准库高效迭代工具链 |

### 常见陷阱

- 子类遗漏 `super().__init__()`。
- `__setattr__` 中 `self.attr = v` 无限递归。
- 生成器耗尽后不能再次遍历。
- `flatten` 未处理字符串导致字符级无限拆分。

属性管理细节见 [08-properties-descriptors.md](08-properties-descriptors.md)。
