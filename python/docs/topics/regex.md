# 正则表达式（re）

正则表达式用于在文本中搜索、匹配、分割和替换模式。Python 通过标准库 `re` 模块提供支持。

## 目录

- [基本语法](#基本语法)
- [re 模块常用函数](#re-模块常用函数)
- [编译与标志位](#编译与标志位)
- [匹配对象与分组](#匹配对象与分组)
- [替换与高级模式](#替换与高级模式)
- [最佳实践](#最佳实践)

## 基本语法

| 元字符 | 含义 |
|--------|------|
| `.` | 除换行符外的任意字符 |
| `\` | 转义特殊字符 |
| `[]` | 字符集（一个字符）；`^` 在开头表示排除；`-` 表示范围 |
| `\|` | 二选一 |
| `()` | 子模式（分组） |
| `?` | 可选（0 次或 1 次） |
| `*` | 0 次或多次 |
| `+` | 1 次或多次 |
| `{n,m}` | n 到 m 次 |
| `^` `$` | 行首 / 行尾锚定 |

**原始字符串**：模式中的反斜杠应使用原始字符串 `r"..."`，避免与 Python 转义冲突。

```python
s1 = "python\\.org"   # Python 转义后变为 python.org
s2 = r"python\.org"   # 正则中 \. 匹配字面量点号
print(s1, s2)
```

## re 模块常用函数

| 函数 | 说明 |
|------|------|
| `compile(pattern[, flags])` | 编译为模式对象，可复用 |
| `search(pattern, string)` | 在字符串任意位置查找首个匹配 |
| `match(pattern, string)` | 仅从字符串开头匹配 |
| `split(pattern, string)` | 按模式分割 |
| `findall(pattern, string)` | 返回所有非重叠匹配列表 |
| `sub(pat, repl, string[, count])` | 替换匹配内容 |
| `escape(string)` | 转义字符串中的正则特殊字符 |

```python
from re import search, compile, match

url_pat = r"(https?://)?(w{3}\.)?python\.org"
py = compile(url_pat)
text = "http://python.org"

print(search(url_pat, text))
print(py.search(text))

print(match("p", "wp"))   # None（不在开头）
print(match("p", "pw"))   # 匹配成功
```

```python
from re import split, compile

txt = "alpha, beta, ,,, gamma delta"
sep = compile(r"[, ]+")
print(sep.split(txt))
print(sep.split(txt, maxsplit=2))
```

```python
from re import findall, sub, escape, match

text = "Everything negative - pressure, challenges - is opportunity."
print(findall(r"[a-zA-Z]+", text))

print(sub(r"\{name\}", "King", "Dear {name} ..."))

raw = "https://www.python.org"
pat = escape(raw)
print(match(pat, raw))
```

## 编译与标志位

频繁使用的模式应 `compile()` 后复用，性能更好。常用标志：

- `re.IGNORECASE` / `re.I`：忽略大小写
- `re.MULTILINE` / `re.M`：多行模式
- `re.VERBOSE` / `re.X`：允许模式中写注释和空白

## 匹配对象与分组

`search()` / `match()` 成功时返回 `Match` 对象：

| 方法 | 说明 |
|------|------|
| `group([n])` | 整个匹配或第 n 个分组 |
| `start([group])` / `end([group])` | 匹配起止位置 |
| `span([group])` | `(start, end)` 元组 |

```python
from re import match

pat = r"There (was a (wee) (cooper)) who (live in Fyfe)"
text = "There was a wee cooper who live in Fyfe"
result = match(pat, text)

print(result.group())    # 完整匹配
print(result.group(1))   # 第一个括号分组
print(result.span(2))    # 第二个分组的位置
```

## 替换与高级模式

### 反向引用

```python
from re import sub

emphasis = r"\*([^*]+)\*"
text = "* who are you? *"
print(sub(emphasis, r"<em>\1</em>", text))
```

### 使用 VERBOSE 提高可读性

```python
from re import compile, VERBOSE

pattern = compile(r"""
    \*       # 起始 *
    ([^*]+)  # 非 * 字符
    \*       # 结束 *
""", VERBOSE)

print(pattern.sub(r"<em>\1</em>", "Hello *python*"))
```

### 非贪婪匹配

```python
from re import compile, VERBOSE

pattern = compile(r"""
    ([*]+)   # 起始标记
    (.+?)    # 非贪婪匹配内容
    \1       # 相同结束标记
""", VERBOSE)

print(pattern.sub(r"<em>\2</em>", "Hello ***python**** This is *it*!"))
```

## 最佳实践

1. **优先用原始字符串**写模式：`r"\d+"` 而非 `"\\d+"`。
2. **复杂或重复使用的模式**用 `compile()` 预编译。
3. **能用简单字符串方法就不用正则**：`str.startswith()`、`in`、`split()` 往往更清晰。
4. **注意贪婪与非贪婪**：默认 `*`、`+` 是贪婪的，需要最少匹配时加 `?`。
5. **验证用户输入时**用 `re.fullmatch()` 确保整串匹配，而非 `search()`。
6. **大文本处理**考虑 `re.finditer()` 逐条迭代，避免 `findall()` 一次性占满内存。
7. **相关标准库**：`argparse`（命令行）、`csv`、`datetime`、`logging`、`itertools` 等常与正则配合使用。
