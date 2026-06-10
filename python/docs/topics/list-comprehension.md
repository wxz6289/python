# 列表推导式与生成器表达式

推导式是 Python 中简洁创建序列的语法糖，本质是表达式而非语句。生成器函数与 `yield` 详见 [10-oop-iterators-generators.md](10-oop-iterators-generators.md)。

## 目录

- [列表推导式](#列表推导式)
- [字典与集合推导式](#字典与集合推导式)
- [生成器表达式](#生成器表达式)
- [最佳实践](#最佳实践)

## 列表推导式

```python
symbols = "abc"

# 传统循环
codes = [ord(sym) for sym in symbols]
print(codes)  # [97, 98, 99]
```

### 带条件过滤

```python
squares = [x * x for x in range(10) if x % 3 == 0]
print(squares)  # [0, 9, 36, 81]
```

### 嵌套推导

```python
pairs = [(x, y) for x in range(3) for y in range(5, 7)]
print(pairs)  # [(0,5),(0,6),(1,5),(1,6),(2,5),(2,6)]
```

等价于：

```python
pairs = []
for x in range(3):
    for y in range(5, 7):
        pairs.append((x, y))
```

### 实用示例：按首字母配对

```python
girls = ["alice", "bernice", "clarice"]
boys = ["chris", "arnold", "bob"]

letter_girls = {}
for g in girls:
    letter_girls.setdefault(g[0], []).append(g)

pairs = [f"{b}/{g}" for b in boys for g in letter_girls.get(b[0], [])]
print(pairs)
```

## 字典与集合推导式

```python
squares_dict = {i: i ** 2 for i in range(10)}
print(squares_dict)

unique_lengths = {len(word) for word in ["hi", "hello", "hey"]}
print(unique_lengths)
```

## 生成器表达式

语法与列表推导类似，但使用圆括号，**惰性求值**，节省内存：

```python
gen = (x * x for x in range(10) if x % 3 == 0)
print(next(gen))  # 0
print(sum(gen))   # 9 + 36 + 81 = 126
```

可直接传给接受可迭代对象的函数：

```python
total = sum(x * x for x in range(10) if x % 3 == 0)
print(total)
```

## 最佳实践

1. **简单映射用推导式**，复杂逻辑用普通循环更清晰。
2. **大数据或只需迭代一次**时用生成器表达式，不要 `[...]` 占内存。
3. **避免过长推导式**（超过一行或嵌套超过两层），可读性下降。
4. **不要用推导式产生副作用**（如 `[print(x) for x in items]`）。
5. **字典推导**适合反转映射、过滤键值对等场景：`{v: k for k, v in d.items()}`。
