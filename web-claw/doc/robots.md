# Robots 协议总结

## 1. Robots 协议是什么

Robots 协议通常指网站根目录下的 `robots.txt` 文件，用于告诉搜索引擎、爬虫、采集程序：哪些路径可以访问，哪些路径不希望被访问。

典型地址：

```text
https://example.com/robots.txt
```

它的核心作用是：**网站向爬虫声明访问规则，爬虫根据规则自我约束**。

需要注意：`robots.txt` 不是安全机制，也不是权限控制。它依赖爬虫主动遵守，不能真正阻止恶意访问。

---

## 2. Robots 协议解决什么问题

### 2.1 降低服务器压力

爬虫如果无限制抓取，可能会频繁请求动态页面、大文件、搜索结果页等，造成服务器压力。

通过 `robots.txt` 可以限制：

- 不抓取后台路径。
- 不抓取搜索结果页。
- 不抓取临时文件。
- 不抓取重复内容页面。

### 2.2 保护不适合公开抓取的页面

网站可能有一些页面虽然能访问，但不希望被搜索引擎收录或被爬虫抓取，例如：

- 管理后台入口。
- 用户中心。
- 订单页面。
- 测试页面。
- 站内搜索结果。

### 2.3 指导搜索引擎建立索引

`robots.txt` 常配合 `Sitemap` 使用，引导搜索引擎抓取更重要的页面。

---

## 3. 基本文件位置和访问规则

### 3.1 必须放在站点根目录

正确：

```text
https://example.com/robots.txt
```

错误：

```text
https://example.com/a/b/robots.txt
```

爬虫通常只会检查域名根目录下的 `robots.txt`。

### 3.2 不同协议和子域名各自独立

下面这些站点的 robots 规则互不等价：

```text
http://example.com/robots.txt
https://example.com/robots.txt
https://www.example.com/robots.txt
https://api.example.com/robots.txt
```

爬虫需要按实际访问的协议、域名分别读取对应的 `robots.txt`。

---

## 4. 基本语法

### 4.1 User-agent

`User-agent` 用于指定规则适用于哪个爬虫。

```txt
User-agent: *
```

含义：适用于所有爬虫。

```txt
User-agent: Googlebot
```

含义：只适用于 Googlebot。

### 4.2 Disallow

`Disallow` 表示不允许抓取的路径。

```txt
User-agent: *
Disallow: /admin/
```

含义：所有爬虫都不允许抓取 `/admin/` 下的内容。

### 4.3 Allow

`Allow` 表示允许抓取的路径，常用于覆盖更宽泛的 `Disallow`。

```txt
User-agent: *
Disallow: /private/
Allow: /private/public.html
```

含义：

- `/private/` 整体不允许抓取。
- 但 `/private/public.html` 允许抓取。

### 4.4 Sitemap

`Sitemap` 用于声明站点地图地址。

```txt
Sitemap: https://example.com/sitemap.xml
```

它不限制抓取权限，只是告诉搜索引擎哪些 URL 更值得发现和索引。

### 4.5 Crawl-delay

`Crawl-delay` 用于建议爬虫两次请求之间间隔多少秒，主要目的是降低爬虫对服务器的访问压力。

示例：

```txt
User-agent: *
Crawl-delay: 10
```

含义：建议所有爬虫每次请求之间至少间隔 10 秒。

也可以只针对某个爬虫设置：

```txt
User-agent: Bingbot
Crawl-delay: 5

User-agent: *
Crawl-delay: 20
```

含义：

- `Bingbot` 建议每 5 秒请求一次。
- 其他爬虫建议每 20 秒请求一次。

需要重点注意：

- `Crawl-delay` 是“抓取频率建议”，不是访问权限规则。
- 它不表示允许或禁止访问某个路径。
- 不同爬虫对它的支持并不一致。
- Googlebot 通常不直接使用 `robots.txt` 中的 `Crawl-delay`，而是通过搜索控制台等方式调节抓取频率。
- Bing、Yandex 等爬虫通常支持该指令。

实践建议：

- 自己写爬虫时应主动尊重 `Crawl-delay`。
- 如果没有 `Crawl-delay`，也应设置合理默认间隔。
- 对同一域名不要高并发请求。
- 遇到 `429 Too Many Requests`、`503 Service Unavailable` 等响应时，应降低频率并退避重试。

---

## 5. 常见 robots.txt 示例

### 5.1 允许所有爬虫访问所有内容

```txt
User-agent: *
Disallow:
```

空的 `Disallow` 表示没有禁止路径。

### 5.2 禁止所有爬虫访问整个站点

```txt
User-agent: *
Disallow: /
```

含义：所有路径都不允许抓取。

### 5.3 禁止抓取后台和搜索页

```txt
User-agent: *
Disallow: /admin/
Disallow: /search
Disallow: /login
```

### 5.4 对不同爬虫设置不同规则

```txt
User-agent: Googlebot
Disallow: /private/

User-agent: *
Disallow: /tmp/
```

含义：

- Googlebot 不允许抓取 `/private/`。
- 其他爬虫不允许抓取 `/tmp/`。

### 5.5 设置抓取间隔

```txt
User-agent: *
Disallow: /admin/
Crawl-delay: 10
```

含义：

- 所有爬虫不允许抓取 `/admin/`。
- 建议爬虫每次请求间隔 10 秒。

---

## 6. 匹配规则重点

### 6.1 路径匹配是前缀匹配

```txt
Disallow: /admin
```

会匹配：

```text
/admin
/admin/
/admin/user
/admin.html
```

如果只想限制目录，建议写成：

```txt
Disallow: /admin/
```

### 6.2 `Allow` 与 `Disallow` 冲突时通常采用更长匹配

示例：

```txt
User-agent: *
Disallow: /docs/
Allow: /docs/public/
```

对于：

```text
/docs/public/a.html
```

`Allow: /docs/public/` 更具体，通常会允许抓取。

### 6.3 通配符支持不完全统一

常见扩展：

```txt
Disallow: /*.pdf$
```

含义通常是禁止抓取 PDF 文件。

但需要注意：

- `*` 和 `$` 不是最早标准中的核心语法。
- 主流搜索引擎一般支持。
- 不同爬虫实现可能有差异。

---

## 7. 爬虫如何使用 robots.txt

一个规范爬虫通常会按以下流程处理：

1. 访问目标站点前，先请求 `/robots.txt`。
2. 解析与自己 `User-agent` 匹配的规则。
3. 判断目标 URL 是否允许抓取。
4. 如果禁止，跳过该 URL。
5. 如果允许，再执行抓取。

伪流程：

```text
GET https://example.com/robots.txt
解析 User-agent 和路径规则
判断 https://example.com/page 是否允许
允许 -> 抓取
禁止 -> 跳过
```

---

## 8. Robots 协议与法律/道德边界

### 8.1 robots.txt 不是访问授权

即使某个页面没有被 `robots.txt` 禁止，也不代表可以任意抓取、复制、商用或高频请求。

仍然需要考虑：

- 网站服务条款。
- 版权限制。
- 隐私信息。
- 反爬策略。
- 数据合规要求。

### 8.2 robots.txt 不是安全防护

不要把敏感路径写入 `robots.txt` 后就认为安全。

例如：

```txt
Disallow: /secret-admin/
```

这反而可能暴露敏感路径。真正的敏感资源必须使用：

- 登录鉴权。
- 权限校验。
- 防火墙。
- 访问控制。

---

## 9. 与 meta robots 的区别

`robots.txt` 控制的是“能不能抓取 URL”。

页面中的 `meta robots` 控制的是“页面能不能被索引、能不能跟踪链接”。

示例：

```html
<meta name="robots" content="noindex,nofollow">
```

含义：

- `noindex`：不要索引该页面。
- `nofollow`：不要跟踪页面里的链接。

区别：

| 方式 | 控制对象 | 生效位置 |
| --- | --- | --- |
| `robots.txt` | 抓取行为 | 网站根目录 |
| `meta robots` | 索引/链接跟踪 | HTML 页面内部 |
| `X-Robots-Tag` | 索引/链接跟踪 | HTTP 响应头 |

---

## 10. 爬虫开发实践建议

### 10.1 必须设置清晰的 User-Agent

不要伪装成浏览器或主流搜索引擎。

建议格式：

```text
MyCrawler/1.0 (+https://example.com/crawler-info)
```

### 10.2 抓取前先检查 robots.txt

对于生产爬虫，建议实现：

- robots 规则缓存。
- 不同域名分别缓存。
- 定期刷新规则。
- 请求失败时保守处理。

### 10.3 控制抓取频率

即使 robots 允许，也应该控制频率：

- 设置请求间隔。
- 如果 robots 中配置了 `Crawl-delay`，优先使用该间隔。
- 限制并发。
- 对 429/503 做退避重试。
- 避免高峰期抓取。

### 10.4 避免抓取无价值或高风险路径

常见应避免路径：

- `/login`
- `/logout`
- `/admin`
- `/cart`
- `/checkout`
- `/search`
- 用户隐私页面
- 动态参数爆炸页面

---

## 11. 常见误区

### 11.1 “robots.txt 禁止了就一定无法访问”

错误。它只是声明规则，不是权限控制。

### 11.2 “robots.txt 没禁止就可以随便爬”

错误。还需要遵守法律、版权、隐私、服务条款和合理频率。

### 11.3 “Disallow 可以防止页面被搜索结果展示”

不完全正确。

如果页面被外部链接引用，搜索引擎可能知道该 URL，但不能抓取页面内容。若要明确禁止索引，应使用：

- `meta robots noindex`
- `X-Robots-Tag: noindex`

### 11.4 “所有爬虫都完全支持同一套规则”

错误。主流爬虫支持较好，但不同爬虫对通配符、优先级、缓存策略可能不同。

---

## 12. 重点总结

- `robots.txt` 是网站给爬虫看的访问规则声明。
- 文件必须放在站点根目录。
- 核心字段是 `User-agent`、`Disallow`、`Allow`、`Sitemap`。
- 它依赖爬虫自觉遵守，不是安全机制。
- 爬虫开发应先读取并遵守 robots 规则。
- 即使 robots 允许，也要控制频率、尊重版权和隐私。
- 真正敏感内容应使用权限控制，而不是依赖 robots。
