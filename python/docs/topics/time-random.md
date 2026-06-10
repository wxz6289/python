# 时间与随机数

涵盖 `time`、`datetime`、`timeit` 和 `random` 模块的常用操作。

## 目录

- [time 模块](#time-模块)
- [datetime 模块](#datetime-模块)
- [timeit 性能测量](#timeit-性能测量)
- [random 模块](#random-模块)
- [最佳实践](#最佳实践)

## time 模块

底层时间操作，返回秒数或 9 元组结构。

| 函数 | 说明 |
|------|------|
| `time()` | 当前时间戳（秒） |
| `localtime([secs])` | 秒数 → 本地时间元组 |
| `asctime([t])` | 时间元组 → 可读字符串 |
| `strptime(string, format)` | 字符串 → 时间元组 |
| `mktime(t)` | 时间元组 → 秒数 |
| `sleep(secs)` | 休眠 |

```python
import time

t = time.localtime()
print(time.asctime(t))

parsed = time.strptime("2024-05-20 10:56:23", "%Y-%m-%d %H:%M:%S")
print(parsed)
print(time.time())
```

## datetime 模块

面向对象的日期时间 API，推荐日常使用。

```python
import datetime as dt

d = dt.date(2024, 5, 20)
t = dt.time(23, 56, 59)
dts = dt.datetime(2024, 5, 21, 10, 23, 36)
print(d, t, dts)
print(dts.ctime())
```

```python
from datetime import date, datetime

now = date.today()
print(now.strftime("%d-%m-%y %b %Y %A"))

birthday = date(1989, 11, 2)
age_days = (now - birthday).days
print(age_days / 365.25)

print(datetime.now().timestamp())
```

> 需要时区时使用 `datetime.timezone` 或第三方库 `zoneinfo`（Python 3.9+ 内置）。

## timeit 性能测量

精确测量小段代码的执行时间。

```python
from timeit import Timer

# 交换变量：元组解包 vs 临时变量
t1 = Timer("a, b = b, a", "a = 1; b = 2").timeit()
t2 = Timer("t = a; a = b; b = t", "a = 1; b = 2").timeit()
print(f"tuple unpack: {t1:.6f}s, temp var: {t2:.6f}s")
```

更完整的性能分析可使用 `profile` / `cProfile` 和 `pstats` 模块。

## random 模块

生成**伪随机数**（非密码学安全）。

| 函数 | 说明 |
|------|------|
| `random()` | [0.0, 1.0) 浮点数 |
| `uniform(a, b)` | [a, b] 均匀分布浮点数 |
| `randrange(start, stop[, step])` | 范围内随机整数 |
| `choice(seq)` | 随机选取一个元素 |
| `shuffle(seq)` | 原地打乱 |
| `sample(seq, k)` | 无重复随机抽样 k 个 |
| `randbytes(n)` | n 个随机字节 |

```python
from random import random, uniform, randrange, choice, shuffle, sample

print(random())
print(uniform(20, 100))
print(randrange(1, 12))

lst = list(range(10))
print(choice(lst))
shuffle(lst)
print(sample(lst, 3))
```

```python
from random import uniform
from time import mktime, localtime, asctime

d1 = mktime((2024, 5, 23, 10, 23, 26, 0, 1, 0))
d2 = mktime((2024, 6, 23, 10, 23, 26, 0, 1, 0))
random_ts = uniform(d1, d2)
print(asctime(localtime(random_ts)))
```

## 最佳实践

1. **日期计算用 `datetime`**，避免手动处理时间元组的 9 个字段。
2. **格式化用 `strftime` / `strptime`**，注意格式码（`%Y` 四位年，`%m` 月等）。
3. **需要可复现的随机序列**时调用 `random.seed(42)`。
4. **密码学场景**（令牌、密钥）用 `secrets` 模块，不用 `random`。
5. **性能对比**用 `timeit`，整体分析用 `cProfile`。
6. **文档测试**可用 `doctest` 验证函数示例：

```python
def average(values):
    """计算算术平均值

    >>> average([2, 3, 7])
    4.0
    """
    return sum(values) / len(values)
```
