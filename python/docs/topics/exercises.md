# 编程练习

本节收录递归与数学相关的练习题及参考实现。

## 目录

- [递归求和](#递归求和)
- [切比雪夫多项式](#切比雪夫多项式)

## 递归求和

### 列表求和

```python
def sum_list(lst):
    if len(lst) == 1:
        return lst[0]
    return lst[0] + sum_list(lst[1:])


def sum_iter(lst):
    result = 0
    for item in lst:
        result += item
    return result


lst = [2, 3, 4, 1, 6, 7, 5, 2]
print(sum_list(lst), sum_iter(lst))
```

### 区间求和

```python
def sum_range(start, end):
    if start == end:
        return start
    return end + sum_range(start, end - 1)


def sum_range_asc(start, end):
    if start == end:
        return end
    return start + sum_range_asc(start + 1, end)


print(sum_range(2, 10), sum_range_asc(2, 10))  # 54, 54
```

## 切比雪夫多项式

第一类和第二类切比雪夫多项式的递推定义：

$$
T_{n}(x) = \begin{cases}
1 & n = 0 \\
x & n = 1 \\
2xT_{n-1}(x)-T_{n-2}(x) & n \geq 2
\end{cases}
$$

$$
U_{n}(x) = \begin{cases}
1 & n = 0 \\
2x & n = 1 \\
2xU_{n-1}(x)-U_{n-2}(x) & n \geq 2
\end{cases}
$$

```python
def chebyshev_t(n, x):
    def t(k, z):
        if k == 0:
            return 1
        if k == 1:
            return z
        return 2 * z * t(k - 1, z) - t(k - 2, z)

    return [t(n, v) for v in x]


def chebyshev_u(n, x):
    def u(k, z):
        if k == 0:
            return 1
        if k == 1:
            return 2 * z
        return 2 * z * u(k - 1, z) - u(k - 2, z)

    return [u(n, v) for v in x]


values = [1, 2, 3, 4, 5]
print(chebyshev_t(0, values))  # [1, 1, 1, 1, 1]
print(chebyshev_t(1, values))  # [1, 2, 3, 4, 5]
print(chebyshev_t(3, values))
print(chebyshev_u(1, values))  # [2, 4, 6, 8, 10]
```

> 生产环境可使用 `numpy.polynomial.chebyshev` 模块。
