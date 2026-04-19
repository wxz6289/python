# Python 异常与处理（整理自 `4.execption.ipynb`）

## 1. 异常是什么

异常（Exception）表示程序运行期间的错误状态。  
如果异常没有被处理，程序会中断并退出。

补充：
- `else`：`try` 中没有异常时执行。
- `finally`：无论是否异常都会执行（适合清理资源）。

---

## 2. 常见内置异常

- `Exception`
- `AttributeError`
- `OSError`
- `IndexError`
- `NameError`
- `SyntaxError`
- `TypeError`
- `KeyError`
- `ValueError`
- `ZeroDivisionError`
- `ModuleNotFoundError`
- `FileNotFoundError`
- `IndentationError`

说明：自定义异常类应直接或间接继承 `Exception`。

---

## 2.1 按语义理解异常分类（更实用）

### 输入与参数错误
- `TypeError`：类型不符合要求
- `ValueError`：值不合法
- `AssertionError`：断言失败（多用于开发期检查）

### 名称、属性与查找错误
- `NameError`：变量未定义
- `AttributeError`：属性不存在
- `LookupError` 抽象基类：
  - `IndexError`：下标越界
  - `KeyError`：键不存在

### 算术与数值错误
- `ArithmeticError` 抽象基类：
  - `ZeroDivisionError`
  - `OverflowError`
  - `FloatingPointError`

### 文件、系统与网络 I/O 错误
- `OSError` 抽象基类：
  - `FileNotFoundError`
  - `PermissionError`
  - `TimeoutError`
  - `ConnectionError` 及其子类（网络连接类问题）

### 导入与运行环境错误
- `ImportError`
- `ModuleNotFoundError`
- `RuntimeError`
- `NotImplementedError`

### 迭代器与生成器相关
- `StopIteration`
- `StopAsyncIteration`

### 不建议业务层直接捕获的异常
- `SystemExit`
- `KeyboardInterrupt`
- `GeneratorExit`

这些属于 `BaseException` 分支，通常应让它们自然退出程序。

---

## 3. 抛出异常（`raise`）

```python
raise ArithmeticError
# raise Exception
# raise Exception("oops!")
```

自定义异常：

```python
class SomeError(Exception):
    pass

raise SomeError("oh!")
```

---

## 4. 异常处理基本模式

### 4.1 `try...except`

```python
try:
    z = int(x) / int(y)
except ZeroDivisionError:
    print("y can't be zero!")
```

### 4.2 捕获多个异常

```python
try:
    z = int(x) / int(y)
except (ZeroDivisionError, ValueError, TypeError) as e:
    print(e)
```

### 4.3 `try...except...else...finally`

```python
try:
    print("A simple task")
except Exception:
    print("something went wrong")
else:
    print("no exception")
finally:
    print("always running")
```

---

## 5. 重新抛出与异常链

### 5.1 捕获后重新抛出

```python
try:
    1 / 0
except ZeroDivisionError:
    print("oops!")
    raise
```

### 5.2 禁用异常上下文

```python
try:
    1 / 0
except ZeroDivisionError:
    raise ValueError from None
```

---

## 5.1 异常传递机制（Propagation）

### 传递的基本规则

- 异常在当前代码块未被捕获时，会沿调用栈“逐层向上传递”。
- 一旦在某一层被匹配的 `except` 捕获，传递会在该层中断。
- 如果最终没有任何一层处理，解释器会输出 traceback 并终止程序。

示例（逐层上传）：

```python
def c():
    1 / 0

def b():
    c()

def a():
    b()

a()  # ZeroDivisionError 从 c -> b -> a -> 顶层
```

### 传播过程中的 `finally`

- 异常向上冒泡时，沿途经过的 `finally` 都会执行。
- 这也是资源清理可靠的原因（文件句柄、连接、锁等）。

```python
def inner():
    try:
        1 / 0
    finally:
        print("inner finally")

def outer():
    try:
        inner()
    finally:
        print("outer finally")

outer()
```

### 捕获后继续传递（重抛）

- 当前层需要记录日志、补充上下文，但不想吞掉异常时，使用 `raise`。

```python
def service():
    try:
        1 / 0
    except ZeroDivisionError:
        print("log: division error")
        raise
```

### 异常转换与因果链

- 业务层常把底层技术异常转换成业务异常，并保留根因：

```python
def parse_amount(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError("金额格式错误") from e
```

---

## 6. 捕获范围建议

不建议裸 `except:`，它会捕获过多异常（包括退出信号）。

```python
except Exception as e:
    print("Invalid input", e)
```

原因：
- `SystemExit`、`KeyboardInterrupt` 来自 `BaseException`，不应被误吞。
- 使用 `Exception` 更安全、可控。

---

## 7. `except` 匹配顺序（非常重要）

异常按“从上到下”匹配，先匹配到就停止。  
因此子类异常要放在父类前面。

```python
class B(Exception): pass
class C(B): pass
class D(C): pass

for cls in [B, C, D]:
    try:
        raise cls()
    except D:
        print("D")
    except C:
        print("C")
    except B:
        print("B")
```

---

## 8. 典型用法示例

### 8.1 循环重试输入

```python
while True:
    try:
        x = int(input("x = "))
        y = int(input("y = "))
        print(x / y)
    except Exception as e:
        print("Invalid input:", e)
    else:
        break
```

### 8.2 按属性可用性做判断

```python
obj = {}
try:
    obj.write
except AttributeError:
    print("The object is not writable")
else:
    print("The object is writable")
```

### 8.3 异常对象信息

```python
try:
    raise Exception("spam", "eggs")
except Exception as inst:
    print(type(inst))
    print(inst.args)
    print(inst)
```

---

## 9. 警告控制（`warnings` 模块）

警告不是异常中断，但可配置为忽略/报错。

```python
from warnings import warn, filterwarnings

filterwarnings("ignore", category=DeprecationWarning)
warn("deprecated", DeprecationWarning)

filterwarnings("error")
warn("something wrong", DeprecationWarning)  # 会按异常处理
```

常见动作：
- `ignore`：忽略警告
- `error`：把警告升级为异常

---

## 10. 实践建议

- 只捕获你能处理的异常。
- 尽量使用精确异常类型，不要滥用 `except Exception`。
- `except` 顺序：子类在前，父类在后。
- 需要继续向上抛时使用 `raise`。
- `finally` 做资源清理；可优先考虑 `with` 管理资源。

---

## 11. 异常处理最佳实践（推荐落地）

### 11.1 分层处理原则

- 底层（DAO/SDK）：抛出技术异常，附带足够上下文。
- 业务层（Service）：将技术异常转换为业务异常。
- 接口层（API/CLI）：统一兜底，输出用户可理解信息。

### 11.2 不吞异常，至少记录日志

```python
import logging

logger = logging.getLogger(__name__)

try:
    do_work()
except Exception:
    logger.exception("do_work failed")
    raise
```

`logger.exception(...)` 会自动携带 traceback。

### 11.3 避免过大的 `try` 块

只包裹“可能出错且需要处理”的语句，减少误捕获。

```python
# 不推荐：把太多逻辑放进同一个 try
try:
    parse()
    validate()
    save()
except ValueError:
    ...
```

### 11.4 业务异常要语义化

```python
class BizError(Exception):
    """业务异常基类"""

class OrderNotFound(BizError):
    pass

class InsufficientBalance(BizError):
    pass
```

相比直接抛 `Exception("失败")`，语义化异常更便于调用方精确处理。

### 11.5 用异常链保留根因

```python
def build_user(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError("用户ID格式非法") from e
```

### 11.6 资源管理优先 `with`

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

相比手写 `try/finally`，`with` 更稳更简洁。

### 11.7 对可重试异常做有限重试

- 仅对瞬时故障重试（网络抖动、超时）。
- 设定重试次数、退避时间、超时边界。
- 不要对参数错误类异常重试（如 `ValueError`）。

### 11.8 API 层统一错误返回

在 Web/API 场景中，建议统一异常到标准响应结构，避免把内部堆栈直接返回给用户。

---

## 12. 反模式补充（高频踩坑）

- `except Exception: pass`：吞异常，后续排障困难。
- 用异常代替正常分支判断（影响可读性和性能）。
- 在库代码中直接 `print` 错误而不抛出。
- 捕获后丢失上下文，不保留原始异常信息。
- 盲目 `retry` 导致雪崩或重复写入。
