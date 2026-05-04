# Python `pprint` 模块总结与最佳实践

`pprint`（pretty-print）是 Python 标准库中用于“美化打印复杂数据结构”的模块。  
当你直接 `print(dict_or_list)` 看不清层级结构时，`pprint` 可以显著提升可读性。

---

## 1. 适用场景

`pprint` 常用于：

- 调试嵌套字典、列表、元组、集合；
- 查看接口返回 JSON（已转成 Python 对象）；
- 排查配置对象、参数对象；
- 在开发阶段快速观察数据结构。

不建议用于：

- 生产日志的最终格式化（建议结构化日志）；
- 大规模高频打印（有性能开销）；
- 面向最终用户的展示输出（建议自定义格式）。

---

## 2. 核心 API

`pprint` 主要有 3 个常用入口：

```python
from pprint import pprint, pformat, PrettyPrinter
```

### 2.1 `pprint(obj, ...)`

直接把对象按更易读的方式打印到标准输出。

```python
from pprint import pprint

data = {"user": {"name": "Alice", "roles": ["admin", "editor"]}, "active": True}
pprint(data)
```

### 2.2 `pformat(obj, ...)`

返回格式化后的字符串（不直接打印）。

```python
from pprint import pformat

text = pformat({"a": [1, 2, 3], "b": {"x": 1}})
print("formatted =", text)
```

适合：

- 写入日志；
- 拼接调试信息；
- 测试断言中对比字符串。

### 2.3 `PrettyPrinter(...)`

创建可复用的格式化器对象，便于统一配置。

```python
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=2, width=100, sort_dicts=False)
pp.pprint({"z": 1, "a": [1, 2, 3]})
```

适合：

- 项目中需要多次按同一规则打印；
- 需要集中管理打印参数。

---

## 3. 常用参数详解

以下参数在 `pprint()` / `pformat()` / `PrettyPrinter` 中都很常用：

### 3.1 `indent`

每层缩进空格数。

```python
pprint(data, indent=2)
```

- 值小：更紧凑；
- 值大：层级更清晰。

### 3.2 `width`

每行最大宽度（近似），超出会换行。

```python
pprint(data, width=80)
```

- `width` 小：换行更多；
- `width` 大：更倾向单行。

### 3.3 `depth`

限制最大显示深度，超出部分显示为 `...`。

```python
pprint(data, depth=2)
```

适合：

- 大对象快速预览；
- 避免递归结构刷屏。

### 3.4 `compact`

更紧凑地排版短元素（尽量同一行）。

```python
pprint(data, compact=True)
```

### 3.5 `sort_dicts`（Python 3.8+ 常用）

是否按 key 排序字典输出。

```python
pprint(data, sort_dicts=False)
```

- `True`：输出稳定，便于比较；
- `False`：保留插入顺序，更贴近真实业务顺序。

### 3.6 `underscore_numbers`（Python 3.10+）

是否给大整数加下划线分组显示。

```python
pprint({"n": 1234567890}, underscore_numbers=True)
```

输出可能类似：

```text
{'n': 1_234_567_890}
```

---

## 4. `print` vs `pprint`

示例对象：

```python
data = {
    "user": {"id": 1, "profile": {"name": "Alice", "skills": ["py", "sql", "ml"]}},
    "orders": [{"id": 101, "amount": 99.5}, {"id": 102, "amount": 188.0}],
}
```

`print(data)` 常常一大行，不利于阅读。  
`pprint(data)` 会自动换行和缩进，层级明显。

一句话：**`print` 更快，`pprint` 更清晰。**

---

## 5. 与 JSON 输出的区别

很多人会把 `pprint` 和 `json.dumps(..., indent=2)` 混用，它们并不相同：

- `pprint`：针对 Python 对象展示，保留 Python 风格（如单引号、`True/False`）。
- `json.dumps`：输出标准 JSON 字符串（双引号、`true/false`、`null`）。

如果要和前端、接口、文件交换数据，优先用 `json.dumps`。  
如果只是本地调试 Python 对象，`pprint` 更方便。

---

## 6. 常见问题

### 6.1 为什么输出顺序变了？

检查是否启用了 `sort_dicts=True`（默认可能为 True/受版本影响）。  
需要保序时明确设置：

```python
pprint(data, sort_dicts=False)
```

### 6.2 为什么还是一行？

可能对象太短，或 `width` 设置较大。  
可尝试减小 `width`，增大 `indent`。

### 6.3 为什么日志里有换行，不好检索？

`pprint` 更适合本地开发调试。  
生产日志建议结构化（JSON 单行 + 字段化）。

---

## 7. 最佳实践

### 7.1 调试阶段优先 `pprint`

对复杂对象（嵌套 dict/list）优先：

```python
pprint(obj, indent=2, width=100, sort_dicts=False)
```

### 7.2 需要拼接日志时用 `pformat`

避免直接多次 `print` 拼接复杂对象：

```python
logger.debug("response=%s", pformat(response_data, width=120))
```

### 7.3 统一团队打印风格

封装一个统一的 `PrettyPrinter`：

```python
PP = PrettyPrinter(indent=2, width=100, sort_dicts=False, compact=False)
```

团队内统一参数，减少“每个人输出格式不一样”的问题。

### 7.4 大对象先限制深度

避免调试时控制台被刷爆：

```python
pprint(big_obj, depth=3)
```

先看结构，再决定是否展开。

### 7.5 接口调试：`json.dumps` 与 `pprint` 分工

- 看 Python 对象结构：`pprint`；
- 输出标准 JSON：`json.dumps(..., ensure_ascii=False, indent=2)`。

### 7.6 避免在高频热路径滥用

`pprint` 会做额外格式化处理。  
高频调用路径（如高 QPS 服务）应谨慎使用，必要时加 debug 开关。

---

## 8. 推荐封装示例

```python
from pprint import PrettyPrinter

PP = PrettyPrinter(
    indent=2,
    width=100,
    depth=None,
    compact=False,
    sort_dicts=False,
)

def pretty(obj, title: str | None = None) -> None:
    if title:
        print(f"\n=== {title} ===")
    PP.pprint(obj)
```

使用：

```python
pretty(data, "用户数据预览")
```

---

## 9. 一句话总结

`pprint` 的核心价值是：**用极低成本把复杂 Python 对象变得“人类可读”**。  
开发调试时非常高效；生产环境要配合日志策略、性能和输出规范合理使用。
