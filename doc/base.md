# Python 核心语法总结

## 1. 基础语法与代码结构

### 1.1 注释与文档字符串
- 单行注释：`# ...`
- 文档字符串（常用于模块、类、函数说明）：`"""..."""`

### 1.2 换行与语句
- 逻辑换行可用反斜杠 `\`，但在 `()`、`[]`、`{}` 中可自然换行。
- 同一行多条语句可用 `;` 分隔（不推荐，影响可读性）。

### 1.3 交互模式变量 `_`
- 在 REPL 中，`_` 通常保存上次表达式结果。
- 建议把它当只读临时值，不要在交互模式中滥用。

## 2. 变量、赋值与作用域基础

### 2.1 命名规则
- 由字母、数字、下划线组成，不能数字开头。
- 区分大小写。
- 不能使用关键字。
- 推荐蛇形命名：`user_name`。

### 2.2 赋值方式
- 普通赋值：`x = 1`
- 多重赋值：`x, y = 1, 2`
- 交换值：`a, b = b, a`
- 删除变量：`del x`

### 2.3 变量与对象
- Python 赋值本质是“名称绑定对象”。
- `a = b` 不会复制对象，只是让 `a` 与 `b` 指向同一对象。

## 3. 数据类型与类型转换

### 3.1 常见内置类型
- 数值：`int`、`float`、`complex`
- 文本：`str`
- 序列：`list`、`tuple`、`range`
- 映射：`dict`
- 集合：`set`
- 二进制：`bytes`、`bytearray`
- 布尔：`bool`
- 空值：`None`

### 3.2 类型判断与转换
- `type(x)`：查看类型
- `int()`、`float()`、`str()`、`list()`、`tuple()`、`dict()`

示例：

```python
print(int("123"))
print(float("3.14"))
print(str(42))
```

## 4. 数值与运算

### 4.1 常见运算符
- 加减乘除：`+ - * /`
- 整除：`//`
- 取余：`%`
- 幂：`**`

### 4.2 其他数字类型
- `decimal.Decimal`：高精度十进制计算
- `fractions.Fraction`：分数精确运算
- `complex`：复数，如 `2 + 3j`

## 5. 字符串（`str`）

### 5.1 特性
- 字符串是不可变对象。
- 支持索引、切片、拼接、重复、成员判断。

### 5.2 创建方式
- 单引号、双引号、三引号。
- 原始字符串：`r"..."`（常用于正则与路径）。

### 5.3 索引与切片
- 索引：`s[i]`，支持负索引
- 切片：`s[start:end:step]`，`end` 不包含

### 5.4 常用方法
- 查找：`find`、`rfind`、`index`
- 分割合并：`split`、`rsplit`、`splitlines`、`join`
- 大小写：`lower`、`upper`、`capitalize`、`title`
- 替换与映射：`replace`、`translate`、`maketrans`
- 去空白：`strip`、`lstrip`、`rstrip`

### 5.5 字符串格式化
- f-string（推荐）
- `str.format(...)`
- `%` 旧式格式化
- `string.Template`

示例：

```python
name, age = "Dreamer", 20
print(f"name: {name}, age: {age}")
print("name: {}, age: {}".format(name, age))
print("name: %s, age: %d" % (name, age))
```

### 5.6 编码与解码
- 编码：`"hello".encode("utf-8")`
- 解码：`b"...".decode("utf-8")`
- `bytes` 不可变，`bytearray` 可变。

## 6. 序列通用操作

序列（字符串、列表、元组等）通常支持：
- `len(seq)`
- 索引与切片
- `+` 拼接，`*` 重复
- `in` / `not in`
- 迭代 `for item in seq`

## 7. 列表（`list`）

### 7.1 特性
- 可变、有序、可重复、可嵌套。

### 7.2 常用操作
- 增：`append`、`extend`、`insert`
- 删：`pop`、`remove`、`del`、`clear`
- 查：`index`、`count`
- 改：索引赋值、切片赋值
- 排序：`sort`（原地）、`sorted`（返回新列表）
- 反转：`reverse`、`reversed`

### 7.3 切片赋值很重要
- 可用于插入、替换、删除子区间。

```python
nums = [1, 5]
nums[1:1] = [2, 3, 4]   # 插入
nums[1:4] = []          # 删除区间
```

## 8. 元组（`tuple`）

### 8.1 特性
- 不可变序列。
- 可作为字典键（前提是元素也可哈希）。

### 8.2 语法细节
- 单元素元组必须带逗号：`(2,)`
- 切片后仍是元组。

### 8.3 解包

```python
data = ("Dreamer", "China", "Python")
name, country, language = data
```

### 8.4 `namedtuple`
- 兼具元组轻量与“字段名可读性”。

## 9. 集合（`set`）

### 9.1 特性
- 无序、元素唯一、可变（`set`）。
- 不支持索引。

### 9.2 常见操作
- 添加：`add`
- 删除：`remove`、`discard`
- 集合运算：并集、交集、差集、对称差集

## 10. 字典（`dict`）

### 10.1 特性
- 键值映射，键必须可哈希且唯一。
- `in` 判断的是“键”。

### 10.2 创建方式
- 字面量：`{"name": "king"}`
- `dict(name="king", age=20)`
- `dict([("name", "king"), ("age", 20)])`

### 10.3 常用方法
- 访问：`d[key]`、`get`
- 视图：`keys`、`values`、`items`
- 删除：`pop`、`popitem`、`del`
- 更新：`update`、`setdefault`
- 复制：`copy`（浅拷贝）

### 10.4 `format_map`
- 用字典做模板填充时可用 `format_map`。

## 11. 引用、浅拷贝、深拷贝

### 11.1 引用赋值
- `b = a`：同一对象引用。

### 11.2 浅拷贝
- `copy.copy(obj)`、`list.copy()`、切片 `[:]`
- 只复制最外层容器，内部嵌套对象仍共享引用。

### 11.3 深拷贝
- `copy.deepcopy(obj)`：递归复制全部层级。

### 11.4 可变默认参数陷阱
- 函数默认参数在定义时求值，只创建一次。
- 推荐用 `None` 作为默认值再在函数内初始化。

```python
def f(items=None):
    if items is None:
        items = []
```

## 12. 面向对象基础

### 12.1 类与对象
- `class` 定义类型，实例通过构造调用创建。
- `__init__` 初始化对象。
- `__del__` 在对象销毁前可能调用（不建议依赖其做关键资源释放）。

### 12.2 继承与 `super()`
- 子类可重写父类方法。
- 重写构造时通常应调用 `super().__init__()`。

### 12.3 静态方法与类方法
- `@staticmethod`：无 `self` / `cls`
- `@classmethod`：首参 `cls`，绑定到类

### 12.4 属性与 `property`
- 可把方法包装成属性接口，统一读写逻辑。

## 13. 魔法方法与协议

### 13.1 容器协议
- `__len__`、`__getitem__`
- 可变容器可实现：`__setitem__`、`__delitem__`

### 13.2 属性访问拦截
- `__getattribute__`、`__getattr__`
- `__setattr__`、`__delattr__`

注意避免无限递归，常通过 `self.__dict__` 或 `super()` 访问底层实现。

### 13.3 `__slots__`
- 可限制实例可绑定属性，减少内存占用。
- 设定后实例默认无 `__dict__`（除非显式加入）。

## 14. 迭代器与生成器

### 14.1 可迭代对象与迭代器
- 可迭代对象：实现 `__iter__`
- 迭代器：实现 `__iter__` 与 `__next__`
- 结束时抛 `StopIteration`

### 14.2 生成器函数
- 含 `yield` 的函数返回生成器。
- 惰性计算，节省内存。

### 14.3 生成器常见方法
- `next(gen)`：取下一个值
- `send(value)`：向生成器发送值
- `close()`：关闭生成器（触发 `GeneratorExit`）
- `throw(...)`：在生成器内部抛异常

### 14.4 生成器表达式

```python
g = (i * i for i in range(10))
print(sum(g))
```

## 15. 核心实践建议

- 优先写清晰代码，再考虑炫技语法。
- 字符串格式化优先用 f-string。
- 需要复制嵌套结构时优先确认是否要 `deepcopy`。
- 函数参数避免可变默认值。
- 对大数据流优先考虑迭代器/生成器，降低内存压力。
- 容器操作优先用内置方法，不重复造轮子。

## 16. 进阶：函数与参数系统

### 16.1 参数类型
- 位置参数、关键字参数、默认参数
- 可变参数：`*args`、`**kwargs`
- 仅位置参数：`/`
- 仅关键字参数：`*`

```python
def f(a, b, /, c, *, d):
    return a + b + c + d
```

### 16.2 闭包与 `nonlocal`
- 内部函数引用外层局部变量形成闭包。
- 需要修改外层变量时用 `nonlocal`。

### 16.3 Lambda 与高阶函数
- `lambda` 适合简短表达式。
- 常见高阶函数：`map`、`filter`、`sorted(key=...)`。

## 17. 进阶：推导式与生成式

### 17.1 推导式
- 列表推导式、集合推导式、字典推导式。

```python
squares = [x * x for x in range(10) if x % 2 == 0]
```

### 17.2 生成器表达式
- 惰性求值，适合大数据场景。

```python
total = sum(x * x for x in range(10_000_000))
```

## 18. 进阶：装饰器

### 18.1 基本装饰器
- 本质：接收函数并返回新函数。

```python
from functools import wraps

def log_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"call: {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper
```

### 18.2 带参数装饰器
- 再包一层工厂函数。

### 18.3 常见内置装饰器
- `@property`、`@staticmethod`、`@classmethod`
- `@dataclass`
- `@lru_cache`

## 19. 进阶：上下文管理器

### 19.1 `with` 语法
- 自动执行资源获取与释放。

```python
with open("a.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

### 19.2 自定义上下文管理器
- 类方式：实现 `__enter__` / `__exit__`
- 生成器方式：`contextlib.contextmanager`

## 20. 高级：异常设计与日志

- 设计清晰的业务异常层次结构。
- 用 `raise ... from ...` 保留根因链路。
- 统一日志入口，记录 `traceback`。
- 面向 API 的错误输出应脱敏，避免泄漏内部堆栈。

## 21. 高级：类型标注与静态检查

### 21.1 类型标注基础
- `list[int]`、`dict[str, int]`、`str | None`
- 泛型：`TypeVar`、`Generic`

### 21.2 常见工具
- `mypy`：静态类型检查
- `ruff` / `flake8`：风格与质量检查
- `black`：格式化

### 21.3 实践建议
- 公共接口、核心模型优先加类型标注。
- 对“边界层”（IO、第三方响应）先校验再入业务逻辑。

## 22. 高级：并发与异步

### 22.1 线程、进程、协程
- 线程：适合 IO 密集型任务。
- 进程：适合 CPU 密集型任务（绕过 GIL）。
- 协程（`asyncio`）：高并发 IO 场景。

### 22.2 `async` / `await`

```python
import asyncio

async def main():
    await asyncio.sleep(1)
    return "ok"
```

### 22.3 选型建议
- Web/网络请求：优先异步协程。
- 数值计算：优先多进程或本地扩展（NumPy/C 扩展）。

## 23. 高级：内存模型与性能优化

### 23.1 名称绑定与对象模型
- Python 变量是“引用”，不是值容器。
- 小对象/短字符串可能有驻留优化（不要依赖 `is` 做值比较）。

### 23.2 垃圾回收
- 引用计数 + 分代回收。
- 循环引用由 GC 处理，但含外部资源时仍要显式释放。

### 23.3 性能实践
- 优先算法与数据结构优化，再做微优化。
- 大量拼接字符串用 `join`，不要循环 `+`。
- 大循环中避免重复属性查找和重复创建临时对象。
- 使用 `timeit`、`cProfile` 做数据驱动优化。

## 24. 高级：工程化与项目结构

### 24.1 包与模块
- 每个目录用 `__init__.py` 显式包化（现代项目可结合命名空间包策略）。
- 避免循环导入，按层次组织依赖方向。

### 24.2 虚拟环境与依赖管理
- 使用 `venv` / `uv` / `poetry` / `pip-tools` 管理依赖。
- 固定依赖版本，区分开发依赖与生产依赖。

### 24.3 测试与质量
- `pytest` 做单元与集成测试。
- 建立 CI：测试、lint、类型检查、格式化。
- 关键代码写回归测试，避免“修复旧 bug 引入新 bug”。

## 25. 综合建议（从会写到写好）

- 先正确，再清晰，再高效。
- 明确边界：输入校验、异常转换、日志记录。
- 让代码“可读、可测、可维护”优先于技巧炫技。
- 在团队中统一代码规范、工具链与项目结构。
