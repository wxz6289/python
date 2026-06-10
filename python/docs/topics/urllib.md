# 网络请求（urllib / requests）

Python 标准库 `urllib` 提供 HTTP 客户端基础能力；生产环境常用第三方库 `requests` 或 `urllib3`。

## 目录

- [urllib.request](#urllibrequest)
- [URL 编码](#url-编码)
- [urllib3](#urllib3)
- [requests](#requests)
- [最佳实践](#最佳实践)

## urllib.request

### 读取网页内容

```python
from urllib.request import urlopen
import re

with urlopen("https://www.python.org") as response:
    content = response.read()

match = re.search(rb'<a href="([^"]+)" .*?>about</a>', content, re.IGNORECASE)
if match:
    print(match.group(1).decode())
```

### 下载文件

```python
from urllib.request import urlretrieve

urlretrieve("https://www.python.org", "./python.html")
```

| 函数 | 说明 |
|------|------|
| `urlretrieve(url, filename)` | 下载到指定路径或临时目录 |
| `urlcleanup()` | 清理临时下载文件 |

## URL 编码

```python
from urllib.parse import quote, unquote, urlencode

qs = quote("你好 hello ? - * ab")
print(qs)
print(unquote(qs))

params = urlencode({"name": "张三", "page": 1})
print(params)
```

> 注意：`urllib.request.quote` 在较新版本中已移至 `urllib.parse`，推荐从 `urllib.parse` 导入。

## urllib3

第三方 HTTP 库，支持连接池、重试等高级特性。

```python
import urllib3

http = urllib3.PoolManager()
response = http.request("GET", "https://www.baidu.com")
print(response.status)
# print(response.data.decode("utf-8"))
```

## requests

更简洁的 HTTP API，社区广泛使用。

```python
import requests

response = requests.get("https://httpbin.org/get", timeout=10)
print(response.status_code)
print(response.json())
```

## 最佳实践

1. **优先用 `requests`** 或 `httpx`（异步场景），代码更简洁。
2. **始终设置超时**：`urlopen(url, timeout=10)` 或 `requests.get(..., timeout=10)`。
3. **用 `with` 管理连接**，确保资源释放。
4. **HTTPS 是默认选择**；注意证书验证，不要随意禁用 SSL 验证。
5. **URL 编码**用 `urllib.parse.quote` / `urlencode`，处理中文和特殊字符。
6. **大文件下载**考虑流式读取（`response.iter_content()`），避免一次性读入内存。
7. **错误处理**：检查状态码，捕获 `urllib.error.URLError` 或 `requests.RequestException`。
