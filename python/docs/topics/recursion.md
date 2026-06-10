# 递归

递归是函数直接或间接调用自身的技术。每个递归算法都需要：

1. **基线条件（base case）**：终止递归
2. **递归步骤**：向基线条件逼近

## 目录

- [阶乘与幂](#阶乘与幂)
- [汉诺塔](#汉诺塔)
- [快速排序](#快速排序)
- [二分查找](#二分查找)
- [最佳实践](#最佳实践)

## 阶乘与幂

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def factorial_iter(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(factorial(10), factorial_iter(10))
```

```python
def power(x, n):
    if n == 0:
        return 1
    return x * power(x, n - 1)


print(power(2, 3))  # 8
```

## 汉诺塔

经典分治问题：将 n 个圆盘从源柱移到目标柱。

```python
def hanoi(n, source, target, auxiliary):
    if n > 0:
        hanoi(n - 1, source, auxiliary, target)
        print(f"Move disk {n} from {source} to {target}")
        hanoi(n - 1, auxiliary, target, source)


hanoi(4, 1, 3, 2)
```

## 快速排序

```python
def quick_sort(items):
    if len(items) <= 1:
        return items
    pivot = items[0]
    smaller = [x for x in items[1:] if x < pivot]
    same = [x for x in items if x == pivot]
    bigger = [x for x in items[1:] if x > pivot]
    return quick_sort(smaller) + same + quick_sort(bigger)


print(quick_sort([22, 16, 2, 42, 5, 3, 11, 78, 32, 21, 66]))
```

> 教学用实现，生产环境应使用内置 `sorted()`。

## 二分查找

前提：序列已排序。

```python
def binary_search(seq, value, lower=0, upper=None):
    if upper is None:
        upper = len(seq) - 1
    if lower > upper:
        raise ValueError(f"{value} not found")
    mid = (lower + upper) // 2
    if seq[mid] == value:
        return mid
    if seq[mid] < value:
        return binary_search(seq, value, mid + 1, upper)
    return binary_search(seq, value, lower, mid - 1)


seq = sorted([23, 12, 56, 21, 90, 32, 49])
print(binary_search(seq, 90))
```

## 最佳实践

1. **确保每次递归都向基线条件靠近**，否则栈溢出（`RecursionError`）。
2. **Python 默认递归深度约 1000**，深度过大时改用迭代或 `sys.setrecursionlimit()`（谨慎使用）。
3. **能用循环清晰表达时优先循环**：阶乘、斐波那契等简单场景迭代更高效。
4. **分治思想**（汉诺塔、快排）是递归的经典应用场景。
5. **尾递归**在 Python 中不会自动优化，不要依赖尾递归性能。
6. **添加清晰的基线条件**，并考虑边界输入（空序列、单元素、已找到等）。
