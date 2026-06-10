# math 与 cmath

`math` 模块提供实数数学函数；`cmath` 模块提供复数数学函数。

## 常用函数

| 模块 | 函数 | 说明 |
|------|------|------|
| `math` | `sqrt(x)` | 平方根（x ≥ 0） |
| `math` | `log(x[, base])` | 对数 |
| `math` | `cos(x)` `sin(x)` | 三角函数（弧度） |
| `math` | `pi` `e` | 数学常量 |
| `math` | `pow(x, y)` | 幂运算 |
| `cmath` | `sqrt(x)` | 复数平方根 |

```python
from math import sqrt, pi, log, cos, pow

print(sqrt(2))
print(round(pi, 3))
print(log(1024, 2))    # 10.0
print(cos(pi / 4))
print(pow(2, 10))
```

```python
from cmath import sqrt

print(sqrt(-1))          # 1j
print((1 + 3j) * (9 + 4j))
```

## 内置 round 与 math

```python
print(round(23.1236, 2))   # 23.12
print(round(32 / 3.3, 2))
print(32 // 3)             # 整除 10
print(3 ** 3)              # 27
print(33 % 12)             # 9
```

## 最佳实践

1. **角度转弧度**：`math.radians(degrees)` / `math.degrees(radians)`。
2. **浮点比较**不要直接用 `==`，用 `math.isclose(a, b)`。
3. **复数运算**用 `cmath`，实数用 `math`（`math.sqrt(-1)` 会报错）。
4. **大数精度**考虑 `decimal` 模块；科学计算考虑 `numpy`。
5. **常量**优先 `math.pi`、`math.e`，不要手写近似值。
