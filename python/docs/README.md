# Python 学习笔记

本目录由 `notebook/` 下的 Jupyter Notebook 整理改写而来，面向 Python 3.10+，内容力求准确、结构清晰，并附有最佳实践示例。

## 基础教程（建议按序阅读）

| 序号 | 文档 | 主题 |
|------|------|------|
| 01 | [基础语法](01-basic-syntax.md) | 注释、变量、类型、数值、字符串 |
| 02 | [语句与控制流](02-statements.md) | if/for/while、match-case、del |
| 03 | [函数](03-functions.md) | 参数、作用域、lambda、装饰器基础 |
| 04 | [标准库概览](04-standard-library.md) | os、sys、argparse、re、random 等 |
| 05 | [异常处理](05-exceptions.md) | try/except、自定义异常、warnings |
| 06 | [模块与包](06-modules.md) | import、`__name__`、`sys.path` |
| 07 | [文件 I/O](07-file-io.md) | open、with、pathlib、JSON |
| 08 | [特性与描述符](08-properties-descriptors.md) | property、staticmethod、`__slots__` |
| 09 | [数据结构](09-data-structures.md) | 序列、列表、元组、字典、集合、拷贝 |
| 10 | [OOP 与迭代](10-oop-iterators-generators.md) | 类、继承、迭代器、生成器 |
| 11 | [上下文管理器](11-context-managers.md) | `with`、协议、`contextlib` |

## 标准库专题

| 文档 | 主题 |
|------|------|
| [collections 扩展](topics/collections.md) | deque、heapq、defaultdict、Counter |
| [标准库补充](topics/stdlib-extra.md) | csv、itertools、subprocess、logging、pickle |
| [正则表达式](topics/regex.md) | re 模块、模式、分组 |
| [sys 与 os](topics/sys-os.md) | 系统接口、环境变量 |
| [时间与随机](topics/time-random.md) | datetime、time、random |
| [urllib](topics/urllib.md) | HTTP 请求基础 |
| [math 模块](topics/math.md) | 常用数学函数 |

## 进阶专题

| 文档 | 主题 |
|------|------|
| [OOP 进阶](topics/oop.md) | MRO、抽象基类、内省（基础见 10） |
| [数据模型](topics/data-model.md) | 魔术方法、协议、运算符重载 |
| [类型检查 mypy](topics/mypy.md) | 类型注解与静态检查 |
| [列表推导](topics/list-comprehension.md) | 推导式语法（生成器详见 10） |
| [排序](topics/sorting.md) | sorted、list.sort、key 函数 |
| [递归](topics/recursion.md) | 递归思想与经典问题 |
| [print 与格式化](topics/print-formatting.md) | 输出与格式化技巧 |
| [asyncio 协程](../asyncio/asyncio.md) | 异步 I/O 与事件循环 |

## 附录（可选）

| 文档 | 主题 |
|------|------|
| [Jupyter](topics/jupyter.md) | Notebook 使用要点 |
| [turtle 绘图](topics/turtle.md) | 海龟绘图入门 |
| [练习](topics/exercises.md) | 综合练习题 |

## 对应关系

| Notebook 源文件 | Markdown 文档 |
|-----------------|---------------|
| `0.basic.ipynb` | 01、09、10 |
| `1.statement.ipynb` | 02 |
| `2.funtion.ipynb` | 03 |
| `3.std.ipynb` | 04 |
| `4.execption.ipynb` | 05 |
| `5.module.ipynb` | 06 |
| `6.file.ipynb` | 07 |
| `7.proprty.ipynb` | 08 |
| 其余 `.ipynb` | `topics/` 下对应文件 |

## 使用说明

- 代码示例可直接复制到 `.py` 文件或 Python REPL 中运行。
- 文档中的「最佳实践」小节总结了常见坑与推荐写法，建议重点阅读。
- 原始 Notebook 仍保留在 `notebook/` 目录，供交互式实验使用；日常查阅以本目录为准。
- 学习进度见 [`todo.md`](../todo.md)。
