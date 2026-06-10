# collections 模块扩展

本文介绍 `collections` 模块中的扩展容器，以及 `heapq` 堆操作。内置 `set` 见 [09-data-structures.md](09-data-structures.md#集合)。

## 目录

- [defaultdict — 默认字典](#defaultdict--默认字典)
- [Counter — 计数器](#counter--计数器)
- [deque — 双端队列](#deque--双端队列)
- [OrderedDict 与 ChainMap](#ordereddict-与-chainmap)
- [堆（heapq）](#堆heapq)
- [最佳实践](#最佳实践)

## defaultdict — 默认字典

访问不存在的键时自动创建默认值，避免手动 `setdefault`：

```python
from collections import defaultdict

dd = defaultdict(list)
dd["fruits"].append("apple")
dd["fruits"].append("banana")
print(dict(dd))  # {'fruits': ['apple', 'banana']}

counts = defaultdict(int)
for word in ["a", "b", "a", "c"]:
    counts[word] += 1
print(dict(counts))  # {'a': 2, 'b': 1, 'c': 1}
```

## Counter — 计数器

对可哈希元素计数，支持集合运算：

```python
from collections import Counter

c = Counter("abracadabra")
print(c)                    # Counter({'a': 5, 'b': 2, 'r': 2, ...})
print(c.most_common(2))     # [('a', 5), ('b', 2)]

c2 = Counter(a=3, b=1)
print(c + c2)               # 合并计数
print(c - c2)               # 减法（结果不含 0 或负数项）
```

## deque — 双端队列

两端 O(1) 追加与弹出，适合队列、滑动窗口：

```python
from collections import deque

q = deque(range(5))
q.append(5)
q.appendleft(6)
print(q.pop(), q.popleft())

q = deque([1, 2, 3, 4, 5])
q.rotate(2)   # 向右旋转
print(q)
```

不要用 `list.pop(0)` 实现队列（O(n)）。

## OrderedDict 与 ChainMap

```python
from collections import OrderedDict, ChainMap

# Python 3.7+ 普通 dict 已有序；OrderedDict 额外提供 move_to_end 等
od = OrderedDict([("a", 1), ("b", 2)])
od.move_to_end("a")

defaults = {"theme": "dark", "lang": "zh"}
user = {"lang": "en"}
config = ChainMap(user, defaults)
print(config["lang"], config["theme"])  # en, dark
```

## 堆（heapq）

堆是**优先队列**：任意顺序插入，随时取出最小元素。Python 用列表表示堆：

| 函数 | 说明 |
|------|------|
| `heappush(heap, x)` | 压入元素 |
| `heappop(heap)` | 弹出最小元素 |
| `heapify(list)` | 原地将列表变为堆 |
| `nlargest(n, iter)` | 最大的 n 个元素 |
| `nsmallest(n, iter)` | 最小的 n 个元素 |

```python
from heapq import heappush, heappop, heapify, nlargest

data = [3, 1, 4, 1, 5, 9]
heap = []
for x in data:
    heappush(heap, x)
print(heappop(heap))  # 1

heapify(data)
print(nlargest(3, data))  # [9, 5, 4]
```

## 最佳实践

1. **"不存在则创建"** 用 `defaultdict` 或 `setdefault`，前者更简洁。
2. **词频/计数** 用 `Counter`，比手动 dict 更清晰。
3. **Top-K 问题** 用 `heapq.nlargest` / `nsmallest`，小数据集比全量排序更高效。
4. **队列场景** 用 `deque`，不要用 `list.pop(0)`。
5. **多层配置合并** 用 `ChainMap`，查找按顺序穿透各层。
