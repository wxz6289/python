# 类型提示与 Mypy

Python 3 通过 `typing` 模块和 [PEP 484](https://peps.python.org/pep-0484/) 支持可选的静态类型注解。Mypy 是最常用的静态类型检查工具。

## 目录

- [快速入门](#快速入门)
- [基本类型](#基本类型)
- [复合类型](#复合类型)
- [协议与 Callable](#协议与-callable)
- [Mypy 工具](#mypy-工具)
- [局限性与最佳实践](#局限性与最佳实践)

## 快速入门

```python
def double(x: int) -> int:
    return x * 2


def greet(name: str) -> None:
    print(f"Hello, {name}")
```

无注解时，参数和返回值默认为动态类型；Mypy 会按实际使用推断，但无法捕获所有错误。

## 基本类型

| 类型 | 说明 |
|------|------|
| `int` `float` `str` `bool` `bytes` | 内置标量类型 |
| `Any` | 任意类型，关闭类型检查 |
| `object` | 所有类型的基类，操作受限 |
| `None` | 仅 `None` 本身 |

`Any` 位于类型层次顶部和底部，与任意类型相容，应谨慎使用。

## 复合类型

| 写法 | 说明 |
|------|------|
| `Optional[T]` 或 `T \| None` | 可为 None |
| `Union[A, B]` 或 `A \| B` | 多种类型之一（Python 3.10+ 推荐 `\|`） |
| `list[int]` | 整数列表 |
| `dict[str, int]` | 字符串键、整数值 |
| `tuple[str, float]` | 固定长度元组 |
| `tuple[int, ...]` | 可变长度元组 |
| `set[frozenset[int]]` | 嵌套集合 |

```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None


def process(value: int | str) -> str:
    return str(value)
```

**泛化容器**还可使用 `collections.abc` 中的 `Sequence`、`Mapping`、`Iterable` 等。

`|` 运算符也可用于 `isinstance()` 和 `issubclass()` 的第二个参数（Python 3.10+）。

## 协议与 Callable

**协议（Protocol）** 是结构化子类型：只要类实现了协议要求的方法，即视为兼容，无需继承。

```python
from typing import Protocol


class Drawable(Protocol):
    def draw(self) -> None: ...


def render(shape: Drawable) -> None:
    shape.draw()
```

**Callable** 注解回调函数：

```python
from typing import Callable

def apply(fn: Callable[[int, int], int], a: int, b: int) -> int:
    return fn(a, b)
```

**NoReturn** 用于永不返回的函数（总是抛异常或无限循环）。

## Mypy 工具

```bash
pip install mypy
mypy your_module.py
```

调试类型推断时使用 `reveal_type()`（仅 Mypy 识别，运行时会报错，需配合检查使用）：

```python
x = [1, 2, 3]
reveal_type(x)  # Mypy: Revealed type is "builtins.list[builtins.int]"
```

参考资料：

- [Mypy 文档](https://mypy.readthedocs.io/)
- [typing 模块文档](https://docs.python.org/zh-cn/3/library/typing.html)

## 局限性与最佳实践

### 静态类型的局限

- **误报与漏报**不可避免
- 拆包、描述符、元类等高级特性支持有限
- 工具滞后于语言新特性
- **业务逻辑错误**（如金额计算错误）类型系统无法捕获

### 最佳实践

1. **类型提示是辅助，不能替代测试**。
2. **渐进式采用**：从新代码或关键模块开始，不必一次注解全项目。
3. **避免过度使用 `Any`**，否则失去检查意义。
4. **优先用内置泛型**（`list[int]`）而非 `List[int]`（Python 3.9+）。
5. **返回值尽量具体**，避免宽泛的 `Union` 返回类型。
6. **用 `Protocol` 表达鸭子类型**，比继承 ABC 更灵活。
7. **CI 中集成 `mypy`**，与单元测试并行运行。
8. **公共 API 优先注解**，内部实现可逐步补充。
