# Jupyter Notebook

Jupyter 是交互式计算环境，支持在浏览器中编写并运行代码单元，即时查看输出。

## 基本用法

```python
x = 2
print(x)
```

每个单元格可独立执行；Shift+Enter 运行当前单元并跳到下一个。

## 魔法命令

以 `%` 或 `%%` 开头的 IPython 魔法命令，扩展 Notebook 功能：

| 命令 | 说明 |
|------|------|
| `%timeit` | 测量单行代码耗时 |
| `%matplotlib inline` | 内嵌显示图表 |
| `%run script.py` | 运行外部脚本 |
| `%alias` | 定义命令别名 |
| `%%writefile file.py` | 将单元格内容写入文件 |

```python
%timeit sum(range(100))
```

## 最佳实践

1. **重启内核 + 从头运行**（Run All）确保 Notebook 可复现。
2. **一个单元格一个逻辑块**，便于调试和分享。
3. **长输出用折叠或限制**，避免 Notebook 文件膨胀。
4. **敏感信息**（API 密钥）不要写入单元格，用环境变量。
5. **生产代码**应提取到 `.py` 模块，Notebook 用于探索和分析。
