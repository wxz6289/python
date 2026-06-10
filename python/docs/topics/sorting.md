# 排序算法

本文介绍两种经典排序算法的实现思路。实际开发中应优先使用内置 `sorted()` 和 `list.sort()`（Timsort，O(n log n)）。

## 目录

- [冒泡排序](#冒泡排序)
- [选择排序](#选择排序)
- [复杂度对比](#复杂度对比)
- [最佳实践](#最佳实践)

## 冒泡排序

相邻元素两两比较，较大者后移，每轮将最大值"冒泡"到末尾。

- **时间复杂度**：O(n²)
- **空间复杂度**：O(1)
- **稳定性**：稳定

```python
from random import randrange


def gen_random_list(n):
    return [randrange(1000) for _ in range(n)]


def bubble_sort(lst):
    length = len(lst)
    if length <= 1:
        return lst
    for i in range(length):
        for j in range(i + 1, length):
            if lst[i] > lst[j]:
                lst[i], lst[j] = lst[j], lst[i]
    return lst


data = gen_random_list(10)
print("before:", data)
bubble_sort(data)
print("after: ", data)
```

可优化：若某轮无交换则提前结束（已有序）。

## 选择排序

每轮在未排序部分找最小值，放到已排序区末尾。

- **时间复杂度**：O(n²)
- **空间复杂度**：O(1)
- **稳定性**：不稳定（交换可能跳过相等元素）

```python
def selection_sort(origin):
    lst = origin.copy()
    length = len(lst)
    if length <= 1:
        return lst
    for i in range(length):
        min_idx = min(range(i, length), key=lambda k: lst[k])
        if min_idx != i:
            lst[i], lst[min_idx] = lst[min_idx], lst[i]
    return lst


data = gen_random_list(10)
print("before:", data)
print("after: ", selection_sort(data))
```

## 复杂度对比

| 算法 | 平均时间 | 最坏时间 | 空间 | 稳定 |
|------|----------|----------|------|------|
| 冒泡排序 | O(n²) | O(n²) | O(1) | 是 |
| 选择排序 | O(n²) | O(n²) | O(1) | 否 |
| 内置 sorted | O(n log n) | O(n log n) | O(n) | 是 |

## 最佳实践

1. **生产代码用 `sorted()` / `list.sort()`**，支持 `key` 和 `reverse` 参数。
2. **需要自定义排序键**时：`sorted(items, key=lambda x: x.name)`。
3. **大数据集**考虑是否只需 Top-K（`heapq.nlargest`）而非全排序。
4. **学习算法**时理解不变量：冒泡维护"尾部有序"，选择维护"头部有序"。
5. **稳定性有要求时**（如先按姓名再按年龄排序）避免不稳定算法，或使用内置排序。
