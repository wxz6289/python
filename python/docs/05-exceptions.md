# 异常

## 目录

- [异常概述](#异常概述)
- [try / except / else / finally](#try--except--else--finally)
- [raise 与异常传播](#raise-与异常传播)
- [自定义异常](#自定义异常)
- [异常链（Exception Chaining）](#异常链exception-chaining)
- [异常匹配顺序与继承层次](#异常匹配顺序与继承层次)
- [warnings 模块](#warnings-模块)
- [常见内置异常](#常见内置异常)
- [最佳实践](#最佳实践)

## 异常概述

程序运行中遇到错误时，Python 会**引发（raise）**一个异常对象。若异常未被捕获，解释器会打印 traceback 并终止程序。

异常是一种**控制流机制**：你可以捕获它、处理它、重新抛出它，或将其转换为更合适的类型。

## try / except / else / finally

四个子句各司其职，应组合使用而非混用裸 `except`：

| 子句 | 执行时机 |
|------|----------|
| `try` | 可能出错的代码 |
| `except` | 捕获并处理指定异常 |
| `else` | **没有**发生异常时执行 |
| `finally` | **无论**是否异常都执行（常用于清理资源） |

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("除数不能为零")
        return None
    else:
        print(f"计算成功: {result}")
        return result
    finally:
        print("divide() 执行完毕")


divide(10, 2)   # 正常路径：走 else
divide(10, 0)   # 异常路径：走 except，finally 仍执行
```

捕获多个异常：`except (KeyError, TypeError) as e:`。**注意**：`else` 块中若再引发异常，不会被同一 `try` 的 `except` 捕获。

## raise 与异常传播

使用 `raise` 主动抛出异常；在 `except` 块中无参 `raise` 会**重新抛出**当前捕获的异常，保留原始 traceback：

```python
class MuffledCalculator:
    def __init__(self, muffled=False):
        self.muffled = muffled

    def calc(self, expr):
        try:
            return eval(expr)
        except ZeroDivisionError:
            if self.muffled:
                print("除零错误已被抑制")
                return None
            raise  # 继续向上传播


calc = MuffledCalculator(muffled=True)
calc.calc("10 / 0")
```

抛出带消息的异常：

```python
raise ValueError("年龄不能为负数")
```

## 自定义异常

自定义异常类必须直接或间接继承 **`Exception`**（不要继承 `BaseException`，那是 `KeyboardInterrupt`、`SystemExit` 等的基类）：

```python
class ValidationError(Exception):
    """输入验证失败"""

    def __init__(self, field, message):
        self.field = field
        super().__init__(f"{field}: {message}")


def set_age(age):
    if age < 0:
        raise ValidationError("age", "不能为负数")
    return age


try:
    set_age(-1)
except ValidationError as e:
    print(e)          # age: 不能为负数
    print(e.field)    # age
```

## 异常链（Exception Chaining）

Python 3 支持显式与隐式异常链：

```python
# 隐式链：raise 新异常时，__context__ 保留原异常
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("数据解析失败") from e

# 显式禁用上下文（traceback 更简洁）
try:
    1 / 0
except ZeroDivisionError:
    raise ValueError("无效输入") from None
```

`raise ... from e` 设置 `__cause__`，表示"直接原因"；`from None` 则隐藏上下文。

## 异常匹配顺序与继承层次

`except` 子句按**从上到下**顺序匹配，**第一个匹配的生效**。子类异常应写在父类**之前**：

```python
class B(Exception):
    pass

class C(B):
    pass

class D(C):
    pass

# 正确：从具体到抽象
for cls in [B, C, D]:
    try:
        raise cls()
    except D:
        print("D")      # 抛出 D 时匹配
    except C:
        print("C")      # 抛出 C 时匹配
    except B:
        print("B")      # 抛出 B 时匹配

# 错误：B 在前，C/D 的 except 永远不会执行
```

若 `except B` 写在 `except D` 之前，抛出 `D()` 时只会匹配到 `B`。

## warnings 模块

警告（`Warning`）用于提示潜在问题，**默认不中断程序**。可通过 `warnings` 模块控制行为：

```python
import warnings

# 忽略某类警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.warn("此 API 即将废弃", DeprecationWarning)

# 将警告提升为异常
warnings.filterwarnings("error", category=UserWarning)
try:
    warnings.warn("严重问题", UserWarning)
except UserWarning as e:
    print(f"警告被当作异常处理: {e}")
```

常用 `filterwarnings` 动作：`"default"`、`"ignore"`、`"error"`、`"always"`、`"once"`。

## 常见内置异常

| 异常类 | 典型场景 |
|--------|----------|
| `Exception` | 所有内置异常的基类（应捕获的最宽泛类型） |
| `TypeError` | 类型不匹配 |
| `ValueError` | 类型正确但值不合法 |
| `KeyError` | 字典键不存在 |
| `IndexError` | 序列索引越界 |
| `AttributeError` | 对象没有该属性 |
| `ZeroDivisionError` | 除零 |
| `FileNotFoundError` | 文件不存在（`OSError` 子类） |
| `ModuleNotFoundError` | 模块找不到 |
| `SyntaxError` / `IndentationError` | 语法/缩进错误 |

完整层次见 [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)。

## 最佳实践

1. **捕获具体异常**，避免裸 `except:` 或宽泛的 `except Exception:`，否则会隐藏 bug。
2. **`else` 用于"成功路径"**，把只在无异常时执行的逻辑放进去，保持 `try` 块尽量小。
3. **`finally` 做清理**，但文件等资源更推荐 `with` 语句（见文件 I/O 文档）。
4. **不要滥用异常做流程控制**，正常分支用 `if/else`，异常留给真正的错误情况。
5. **自定义异常要有意义**，提供足够上下文（字段名、错误码等），便于上层处理。
6. **重新抛出时保留 traceback**：用无参 `raise`，不要随意 `raise e`（Python 2 风格，会丢失栈信息）。
7. **warnings 与 exceptions 分工明确**：可恢复的预期问题用 warning，必须处理的错误用 exception。
