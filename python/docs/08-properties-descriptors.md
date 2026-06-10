# 特性、描述符与类方法

`property`、描述符协议、`@property` 装饰器、`staticmethod`、`classmethod` 与 `__slots__` 是 Python 管理类属性的核心机制。

## 目录

1. [property 基础](#property-基础)
2. [@property 装饰器](#property-装饰器)
3. [属性删除 deleter](#属性删除-deleter)
4. [描述符协议](#描述符协议)
5. [描述符工厂与 __set_name__](#描述符工厂与-__set_name__)
6. [覆盖型与非覆盖型描述符](#覆盖型与非覆盖型描述符)
7. [staticmethod 与 classmethod](#staticmethod-与-classmethod)
8. [属性内省与特殊方法](#属性内省与特殊方法)
9. [__slots__](#__slots__)
10. [最佳实践](#最佳实践)

---

## property 基础

通过 getter/setter 定义的属性称为**特性**。`property(fget, fset, fdel, doc)` 根据参数决定可读写、可删除及文档。

**关键**：setter 必须写私有存储属性（`self._weight`），不能写 `self.weight`，否则无限递归。

```python
class LineItem:
    def __init__(self, description, weight, price):
        self.description = description
        self._weight = weight
        self._price = price

    def get_weight(self):
        return self._weight

    def set_weight(self, value):
        if value > 0:
            self._weight = value   # 写 _weight，不是 weight
        else:
            raise ValueError("value must be > 0")

    weight = property(get_weight, set_weight)

    def subtotal(self):
        return self._weight * self._price


li = LineItem("Apple", 12, 1.2)
li.weight = 20
print(li.subtotal())   # 240.0
```

---

## @property 装饰器

推荐写法，配合 `@name.setter` / `@name.deleter`：

```python
class Rectangle:
    def __init__(self, w, h):
        self._width, self._height = w, h

    @property
    def size(self):
        """返回 (宽, 高)。"""
        return self._width, self._height

    @size.setter
    def size(self, value):
        self._width, self._height = value

    @property
    def area(self):
        return self._width * self._height


r = Rectangle(12, 23)
r.size = (120, 230)
print(r.area)   # 27600
```

特性定义在**类**上，优先级高于实例 `__dict__` 同名键；只读属性不提供 setter。

### 最佳实践

存储用 `_name`，对外暴露 `@property`；验证逻辑放 setter。

---

## 属性删除 deleter

```python
class BlackKnight:
    def __init__(self):
        self.phrases = [("an arm", "'Tis but a scratch."),
                        ("a leg", "I'm invincible!")]

    @property
    def member(self):
        return self.phrases[0][0]

    @member.deleter
    def member(self):
        lost, text = self.phrases.pop(0)
        print(f"loses {lost} -- {text}")


knight = BlackKnight()
del knight.member
```

---

## 描述符协议

实现 `__get__`、`__set__` 或 `__delete__` 之一即为**描述符**。`property`、`staticmethod`、`classmethod`、`super` 均基于此机制。

| 方法 | 触发时机 |
|------|----------|
| `__get__(self, instance, owner)` | 读取 |
| `__set__(self, instance, value)` | 赋值 |
| `__delete__(self, instance)` | 删除 |

```python
class Quantity:
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __get__(self, instance, owner):
        return self if instance is None else instance.__dict__[self.storage_name]

    def __set__(self, instance, value):
        if value > 0:
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError(f"{self.storage_name} must be > 0")


class LineItem:
    weight = Quantity("weight")
    price = Quantity("price")

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price
```

---

## 描述符工厂与 __set_name__

Python 3.6+ 用 `__set_name__` 自动获取属性名，避免手动传入存储名：

```python
class Quantity:
    def __set_name__(self, owner, name):
        self.storage_name = name

    def __get__(self, instance, owner):
        return self if instance is None else instance.__dict__[self.storage_name]

    def __set__(self, instance, value):
        if value > 0:
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError(f"{self.storage_name} must be > 0")

class LineItem:
    weight = Quantity()
    price = Quantity()
```

---

## 覆盖型与非覆盖型描述符

| 类型 | 条件 | 行为 |
|------|------|------|
| 覆盖型 | 有 `__set__` 或 `__delete__` | 赋值走描述符，不走实例 `__dict__` |
| 非覆盖型 | 仅 `__get__` | 实例 `__dict__` 同名键优先 |

`property` 是覆盖型；无 setter 的 `property` 赋值抛 `AttributeError`。

---

## staticmethod 与 classmethod

| 类型 | 第一参数 | 典型用途 |
|------|---------|----------|
| 实例方法 | `self` | 操作实例状态 |
| `@staticmethod` | 无 | 与类相关但不访问实例/类 |
| `@classmethod` | `cls` | 工厂方法、访问类属性 |

```python
class MyClass:
    count = 0

    @staticmethod
    def validate(v):
        return v > 0

    @classmethod
    def create(cls, value):
        obj = cls.__new__(cls)
        obj.value = value
        cls.count += 1
        return obj

obj = MyClass.create(42)
```

### 最佳实践

纯工具函数放模块级；多态构造用 `@classmethod`。

---

## 属性内省与特殊方法

| 工具/方法 | 说明 |
|-----------|------|
| `vars(obj)` / `dir(obj)` | 实例字典 / 属性列表 |
| `getattr` / `setattr` / `hasattr` | 动态访问属性 |
| `__getattribute__` | 每次访问都调用 |
| `__getattr__` | 常规查找失败后的兜底 |
| `__setattr__` / `__delattr__` | 赋值 / 删除拦截 |

直接写 `obj.__dict__["key"]` 不触发描述符。`__setattr__` 中应写 `self.__dict__[name] = value`；`__getattribute__` 中用 `super().__getattribute__(name)`。

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
```

特殊方法定义在**类**上，实例 `__dict__` 无法遮盖。

---

## __slots__

固定实例属性名，省略 `__dict__`，节省内存。

```python
class Pixel:
    __slots__ = ("x", "y")

class OpenPixel(Pixel):
    pass

p = Pixel()
p.x, p.y = 10, 20
# p.color = "red"   # AttributeError

op = OpenPixel()
op.color = "green"   # 子类无 __slots__，仍有 __dict__
```

| 要点 | 说明 |
|------|------|
| 无 `__dict__` | 不能动态添加未声明属性 |
| 子类 | 未定义 `__slots__` 则保留 `__dict__` |
| 恢复动态属性 | `__slots__` 中加入 `"__dict__"` |
| `vars()` | 无 `__dict__` 时失败，`dir()` 仍可用 |

---

## 最佳实践

| 场景 | 推荐 |
|------|------|
| 简单验证 | `@property` + setter |
| 多类复用验证 | 描述符 + `__set_name__` |
| 只读派生值 | 仅 `@property` |
| 工厂构造 | `@classmethod` |
| 大量小对象 | `__slots__` |
| 存储命名 | 内部 `_attr`，对外 `attr` |

**避免**：setter 写 `self.attr`（递归）；`__getattribute__` 中直接 `self.attr`（递归）；对需动态扩展的类用 `__slots__`。
