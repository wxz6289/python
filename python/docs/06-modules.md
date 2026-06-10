# 模块与包

## 目录

- [模块概述](#模块概述)
- [导入方式](#导入方式)
- [包与导入规则](#包与导入规则)
- [__name__ 与 __main__](#__name__-与-__main__)
- [模块搜索路径 sys.path](#模块搜索路径-syspath)
- [__all__ 公开接口](#__all__-公开接口)
- [importlib.reload 重新加载](#importlibreload-重新加载)
- [常用模块内省](#常用模块内省)
- [最佳实践](#最佳实践)

## 模块概述

模块（module）是包含 Python 代码的 `.py` 文件，用于组织可复用的函数、类和变量。

- 模块在**首次被导入**时执行一次，之后复用已加载的对象。
- 导入时会在同目录生成 `__pycache__/`，存放编译后的字节码（`.pyc`）。
- 每个模块有独立的全局命名空间；其中定义的名称成为模块的**属性**。

```bash
# 以模块方式运行（会设置 __name__ == "__main__"）
python -m mypackage.mymodule arg1 arg2
```

## 导入方式

Python 提供多种 import 语法，按可读性与命名空间污染程度选择：

```python
import math                          # 导入整个模块
import numpy as np                  # 别名，避免名称冲突
from math import sqrt, pi           # 导入模块中的特定名称
from collections import OrderedDict as OD  # 为导入项起别名
```

| 写法 | 访问方式 | 适用场景 |
|------|----------|----------|
| `import mod` | `mod.func()` | 最常用，命名空间清晰 |
| `import mod as m` | `m.func()` | 长模块名或避免冲突 |
| `from mod import func` | `func()` | 频繁调用、名称无歧义 |
| `from mod import func as f` | `f()` | 避免与本地名称冲突 |

**避免** `from module import *`：污染命名空间，且无法静态分析依赖。若模块定义了 `__all__`，`*` 只会导入其中列出的名称，但仍不推荐在生产代码中使用。

```python
# 不推荐
from os.path import *

# 推荐
from os.path import join, exists
```

## 包与导入规则

包（package）是包含 `__init__.py`（Python 3.3+ 也支持 namespace package，但显式 `__init__.py` 仍是常见做法）的目录，用于组织相关模块。

```
mypackage/
    __init__.py
    utils.py
    models/
        __init__.py
        user.py
```

**两种导入路径的语义不同：**

```python
# 点号路径：除最后一项外必须都是包；最后一项是模块或子包
import mypackage.utils
import mypackage.models.user

# from ... import：item 可以是子模块，也可以是包内定义的函数/类/变量
from mypackage import utils
from mypackage.utils import helper
from mypackage.models.user import User
```

规则摘要：

- `import pkg.mod.submod`：中间每一级必须是包，最后一级是模块或包。
- `from pkg import item`：先在 `pkg` 中查找 `item`；若未找到，再尝试加载 `pkg/item.py` 或 `pkg/item/`。
- 不能用 `import pkg.some_function` 导入包内**直接定义**的函数——函数不是模块，应使用 `from pkg import some_function`。

## __name__ 与 __main__

每个模块都有 `__name__` 属性：

- 被 **import** 时：`__name__` 为模块的完整名称（如 `"mypackage.utils"`）。
- 被 **直接运行** 时：`__name__` 为 `"__main__"`。

惯用法——将"可被导入的代码"与"脚本入口"分离：

```python
# mymodule.py
def main():
    print("程序入口逻辑")


def helper():
    return 42


if __name__ == "__main__":
    main()
```

这样其他模块 `import mymodule` 时不会执行 `main()`，而 `python mymodule.py` 会执行。

## 模块搜索路径 sys.path

解释器按 `sys.path` 列表**顺序**查找模块：

1. 脚本所在目录（或当前工作目录）
2. `PYTHONPATH` 环境变量中的目录
3. 标准库目录
4. site-packages（第三方包）

```python
import sys
from pprint import pprint

pprint(sys.path)

# 临时添加搜索路径（仅在当前进程有效）
sys.path.insert(0, "/path/to/my/projects")
```

更推荐的方式：将项目安装为包（`pip install -e .`），或使用 `PYTHONPATH`，而非在代码中硬编码路径。

## __all__ 公开接口

`__all__` 定义模块的**公开 API**，影响 `from module import *` 的行为，也作为文档约定：

```python
# mymodule.py
__all__ = ["public_func", "PublicClass"]

def public_func():
    pass

def _internal_helper():
    pass

class PublicClass:
    pass
```

未列入 `__all__` 的名称（尤其以下划线开头的）视为内部实现，外部代码不应依赖。

## importlib.reload 重新加载

模块默认只导入一次。开发调试时可用 `reload` 强制重新执行模块代码：

```python
import importlib
import mymodule

importlib.reload(mymodule)
```

**注意**：

- 仅重新加载**该模块**本身，不会递归 reload 其依赖。
- reload 前创建的对象（如类的实例）与 reload 后的类**不是同一类型**。
- 生产环境不应使用 reload；仅适合交互式调试。

## 常用模块内省

`dir(obj)` 列出属性；`help(obj)` 查看文档；`obj.__doc__` 获取 docstring；`module.__file__` 获取源文件路径；`sys.modules` 查看已加载模块；`sys.argv` 获取命令行参数。

## 最佳实践

1. **优先 `import module`**，只在频繁使用且名称清晰时用 `from ... import`。
2. **禁止 `import *`**，明确列出所需名称。
3. **用 `if __name__ == "__main__":` 保护脚本入口**，使模块可测试、可复用。
4. **包结构扁平清晰**，避免循环导入；若出现循环，将共享依赖抽到第三个模块。
5. **用 `__all__` 声明公开 API**，内部函数以下划线前缀命名。
6. **路径管理用安装机制**（`pyproject.toml` + `pip install -e .`），而非到处 `sys.path.append`。
7. **第三方包用 pip/conda 安装**，不要手动复制 `.py` 到项目目录。
8. **reload 仅限调试**，不要在生产代码或测试中依赖它。
