# OOP 进阶

> 类的基础、继承、多态、迭代器与生成器见 [10-oop-iterators-generators.md](10-oop-iterators-generators.md)。本文聚焦多重继承、MRO、抽象基类与内省。

## 目录

- [内省与类型检查](#内省与类型检查)
- [名称改写与类属性陷阱](#名称改写与类属性陷阱)
- [多重继承与 MRO](#多重继承与-mro)
- [抽象基类](#抽象基类)
- [最佳实践](#最佳实践)

## 内省与类型检查

| 函数 | 说明 |
|------|------|
| `callable(obj)` | 对象是否可调用 |
| `getattr(obj, name[, default])` | 获取属性 |
| `setattr(obj, name, value)` | 设置属性 |
| `hasattr(obj, name)` | 是否拥有属性 |
| `isinstance(obj, cls)` | 是否为某类（或其子类）的实例 |
| `issubclass(A, B)` | A 是否为 B 的子类 |
| `type(obj)` | 返回对象类型 |

```python
from inspect import isclass

print(hasattr(tuple, "append"), hasattr(list, "append"))
print(callable(getattr(list, "append", None)))

p = object()
setattr(p, "name", "example")
print(p.name, isclass(type(p)))  # example True
```

## 名称改写与类属性陷阱

双下划线 `__` 开头的名称触发**名称改写**（name mangling），在类外变为 `_ClassName__attr`，并非真正的私有：

```python
class Secretive:
    def __inaccessible(self):
        print("内部方法")

    def accessible(self):
        self.__inaccessible()

s = Secretive()
s.accessible()
# s._Secretive__inaccessible()  # 可访问，但不推荐依赖
```

**类属性陷阱**：给实例赋同名属性不会修改类属性：

```python
class MemberCounter:
    members = 0

    def __init__(self):
        MemberCounter.members += 1

m1 = MemberCounter()
m2 = MemberCounter()
print(MemberCounter.members)  # 2

m1.members = "hi"  # 新建实例属性
print(m2.members, m1.members)  # 2, hi
```

## 多重继承与 MRO

多个超类实现同名方法时，**方法解析顺序（MRO）** 决定调用哪个。Python 3 使用 C3 线性化，通过 `Class.__mro__` 查看：

```python
class Calculator:
    def calculate(self, expression):
        self.value = eval(expression)


class Talker:
    def talk(self):
        print(f"Hi, value is: {self.value}")


class TalkingCalculator(Calculator, Talker):
    pass


tc = TalkingCalculator()
tc.calculate("1 + 2 * 3")
tc.talk()
print(TalkingCalculator.__mro__)
```

> `eval()` 仅用于演示，生产代码应使用安全的表达式解析。

## 抽象基类

抽象类规定子类必须实现的方法，自身不能实例化：

```python
from abc import ABC, abstractmethod


class Talker(ABC):
    @abstractmethod
    def talk(self):
        pass


class Dog(Talker):
    def talk(self):
        print("Woof!")


class Herring:
    def talk(self):
        print("Blub!")


d = Dog()
print(isinstance(d, Talker))  # True

h = Herring()
print(isinstance(h, Talker))  # False

Talker.register(Herring)  # 虚拟子类，失去抽象方法保障
print(isinstance(h, Talker))  # True
```

## 最佳实践

1. **优先组合而非继承**：用"有一个"代替"是一个"。
2. **慎用多重继承**：仅在 mixin 等明确场景使用，注意 MRO 顺序。
3. **用 `super()` 调用超类**：多重继承中避免硬编码父类名。
4. **约定式私有**：单下划线 `_attr` 表示内部使用；双下划线触发名称改写。
5. **需要接口契约时用 `abc`** 或 `typing.Protocol`，而非仅靠文档约定。
