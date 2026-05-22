# 框架对比：FastAPI vs Flask / Django / Spring / NestJS

本文对比 **FastAPI** 与 Flask、Django、Spring Boot、NestJS 的定位、写法与选型，并结合本仓库 [ai-server](../README.md) 说明为何选用 FastAPI。

相关学习材料：[FastAPI 核心内容](./fastapi.md) · [3 天学习计划](./fastapi-learning-plan.md)

---

## 1. 一句话定位

| 框架 | 语言 | 定位 |
|------|------|------|
| **FastAPI** | Python | 现代 API 框架，类型驱动 + 异步 + 自动 OpenAPI |
| **Flask** | Python | 微框架，灵活极简，生态靠扩展 |
| **Django** | Python | 全栈 Web 框架，ORM/Admin/模板一体化 |
| **Spring Boot** | Java/Kotlin | 企业级后端，完整 IoC/DI 生态 |
| **NestJS** | TypeScript | Node 企业级框架，装饰器 + DI，类 Spring |

## 2. 核心维度对比

| 维度 | FastAPI | Flask | Django | Spring Boot | NestJS |
|------|---------|-------|--------|-------------|--------|
| **设计哲学** | API 优先 | 微框架、自由组合 | 全栈、约定优于配置 | 企业级、分层清晰 | 模块化、AOP + DI |
| **协议** | ASGI（异步） | WSGI（同步为主） | WSGI/ASGI（3.x 支持 async） | Servlet / WebFlux（响应式） | Node HTTP（Express/Fastify） |
| **异步** | ✅ 原生 `async/await` | ⚠️ 需扩展或 2.x+ 有限支持 | ⚠️ 3.1+ 逐步支持 | ✅ WebFlux 响应式栈 | ✅ 原生 Promise/async |
| **数据校验** | Pydantic 内置 | 需 Marshmallow / WTForms | Serializer / Form | Bean Validation (`@Valid`) | class-validator + Pipe |
| **依赖注入** | `Depends()`（轻量） | 无内置，手动或扩展 | 无内置 DI 容器 | Spring IoC 容器（完整） | `@Injectable()` 容器（完整） |
| **ORM** | 无内置，自选 SQLAlchemy 等 | 无内置 | **Django ORM** 内置 | **JPA/Hibernate** | TypeORM / Prisma 等 |
| **Admin 后台** | 无 | 无 | ✅ **Django Admin** | 需第三方 | 需第三方 |
| **API 文档** | ✅ 自动生成 Swagger/ReDoc | 需 flask-swagger 等 | DRF 可生成 | springdoc-openapi | `@nestjs/swagger` 装饰器 |
| **性能** | 高（异步 I/O） | 中 | 中 | 高（JVM 优化后） | 高 |
| **学习曲线** | 低～中 | 低 | 中～高 | 高 | 中～高 |
| **适用场景** | REST API、AI 服务、微服务 | 小型 Web/API、脚本服务 | 内容站、CMS、全栈 | 大型 enterprise、金融 | TS 全栈后端、微服务 |

## 3. 同一接口：Hello + 查询参数

**FastAPI**

```python
@app.get("/hello")
async def hello(name: str = "world") -> dict:
    return {"message": f"Hello {name}"}
```

**Flask**

```python
@app.route("/hello")
def hello():
    name = request.args.get("name", "world")
    return {"message": f"Hello {name}"}
```

**Django（DRF）**

```python
class HelloView(APIView):
    def get(self, request):
        name = request.query_params.get("name", "world")
        return Response({"message": f"Hello {name}"})
```

**Spring Boot**

```java
@GetMapping("/hello")
public Map<String, String> hello(@RequestParam(defaultValue = "world") String name) {
    return Map.of("message", "Hello " + name);
}
```

**NestJS**

```typescript
@Get('hello')
hello(@Query('name') name = 'world') {
  return { message: `Hello ${name}` };
}
```

> FastAPI / NestJS / Spring 的参数都带类型；Flask / Django 需手动从 `request` 取值并自行校验。

## 4. 请求体校验对比

| 框架 | 写法 | 校验失败响应 |
|------|------|--------------|
| FastAPI | Pydantic `BaseModel` 作参数 | 422 + 字段级错误 |
| Flask | Marshmallow schema 手动 `.load()` | 自定义 |
| Django | DRF `Serializer` | 400 |
| Spring | `@Valid @RequestBody UserDto` | 400 |
| NestJS | DTO class + `ValidationPipe` | 400 |

**FastAPI**

```python
class UserCreate(BaseModel):
    name: str
    email: EmailStr

@app.post("/users")
async def create_user(user: UserCreate):
    return user
```

**NestJS**

```typescript
class CreateUserDto {
  @IsString() name: string;
  @IsEmail() email: string;
}

@Post('users')
create(@Body() dto: CreateUserDto) { return dto; }
```

**Spring Boot**

```java
public record UserCreate(@NotBlank String name, @Email String email) {}

@PostMapping("/users")
public UserCreate create(@Valid @RequestBody UserCreate body) {
    return body;
}
```

## 5. 依赖注入对比

| 框架 | 机制 | 特点 |
|------|------|------|
| **FastAPI** | `Depends(get_db)` | 按请求解析，无全局容器；简单场景够用 |
| **Flask** | 无 | 常用 `g`、工厂模式或 `flask-injector` |
| **Django** | 无 | 视图函数直接 import；Service 层靠约定 |
| **Spring** | `@Autowired` / 构造器注入 | 完整 IoC，生命周期管理、AOP |
| **NestJS** | 构造函数注入 | Module + Provider，与 Spring 最像 |

**FastAPI — 数据库依赖**

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

**NestJS — 同等模式**

```typescript
@Injectable()
class ItemsService {
  constructor(private readonly repo: ItemRepository) {}
}

@Get('items')
findAll(@Inject(ItemsService) svc: ItemsService) {
  return svc.findAll();
}
```

**Spring Boot**

```java
@RestController
@RequiredArgsConstructor
public class ItemController {
    private final ItemService itemService;

    @GetMapping("/items")
    public List<Item> list() {
        return itemService.findAll();
    }
}
```

## 6. 概念映射表

| 概念 | FastAPI | Flask | Django | Spring Boot | NestJS |
|------|---------|-------|--------|-------------|--------|
| 路由 | `@app.get()` / `APIRouter` | `@app.route()` / Blueprint | `urls.py` / View | `@GetMapping` | `@Get()` + `@Controller()` |
| 中间件 | `@app.middleware("http")` | `@app.before_request` | Middleware 类 | `Filter` / `Interceptor` | `@UseGuards` / Middleware |
| 鉴权 | `Depends(get_user)` | `@login_required` / 扩展 | `@permission_required` | Spring Security | `@UseGuards(AuthGuard)` |
| 异常 | `@app.exception_handler` | `@app.errorhandler` | DRF exception handler | `@ControllerAdvice` | `@Catch()` / Filter |
| 配置 | `pydantic-settings` | `app.config` | `settings.py` | `application.yml` | `@nestjs/config` |
| 项目组织 | `APIRouter` 分包 | Blueprint | App 分应用 | Package 分层 | `@Module()` |
| 生命周期 | `lifespan` | 无标准 | AppConfig.ready | `@PostConstruct` | `onModuleInit` |

## 7. 请求生命周期对比

**FastAPI / Starlette**

```
请求 → 中间件 → 路由匹配 → Depends 解析 → Pydantic 校验 → 路由函数 → 响应
```

**NestJS**

```
请求 → Middleware → Guard → Interceptor(前) → Pipe → Controller → Service → Interceptor(后) → Filter
```

**Spring Boot（Servlet）**

```
请求 → Filter → DispatcherServlet → Interceptor → Controller → Service → Repository → 响应
```

**Flask**

```
请求 → before_request → 视图函数 → after_request → 响应
```

**Django**

```
请求 → Middleware 链 → URL 路由 → View →（ORM）→ 响应
```

NestJS 与 Spring 的管道最完整；FastAPI 用 Depends + 中间件覆盖大部分场景，但没有 NestJS 那样细分的 Guard/Interceptor 层级。

## 8. 性能与并发模型

| 框架 | 并发模型 | 说明 |
|------|----------|------|
| FastAPI | 单进程 async 事件循环 | I/O 密集（API、AI 调用）表现好 |
| Flask | WSGI 同步，多 worker 扩展 | 默认阻塞；高并发靠 gunicorn 多进程 |
| Django | WSGI/ASGI | 传统同步为主；Channels 支持 WebSocket |
| Spring Boot | 线程池（Servlet）或 Reactor（WebFlux） | JVM 多线程成熟；WebFlux 适合高并发 I/O |
| NestJS | Node 单线程事件循环 | 与 FastAPI 类似；CPU 密集需 Worker |

**AI 服务场景**（如本仓库 `ai-server`）：FastAPI 与 NestJS 都适合 I/O 等待 LLM 响应；Flask/Django 需多 worker 或异步改造；Spring WebFlux 也可但 Java 生态偏重。

## 9. 选型建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| **纯 REST / OpenAPI API** | FastAPI | 文档、校验、async 开箱即用 |
| **Python AI / ML 服务** | FastAPI | 与 LangChain、Pydantic 生态契合 |
| **小型脚本 / 原型** | Flask | 最少样板代码 |
| **CMS / 管理后台 / 全栈** | Django | Admin + ORM + 模板一体 |
| **大型企业 / 多团队 Java** | Spring Boot | 成熟 DI、Security、事务、监控 |
| **TypeScript 全栈 / 已有 Node 基建** | NestJS | 与前端 TS 统一，模块化强 |
| **从 Spring 迁移到 Node** | NestJS | 概念最接近 |
| **从 Flask 升级到现代 Python API** | FastAPI | 迁移成本低，语法仍简洁 |

## 10. 与本项目（ai-server）的对照

当前 `main.py` 若用其他框架实现，大致对应：

| 能力 | FastAPI（现状） | Flask 等价 | NestJS 等价 |
|------|-----------------|------------|-------------|
| GET `/chat` | `@app.get` + query 参数 | `@app.route` + `request.args` | `@Get()` + `@Query()` |
| 纯文本响应 | `PlainTextResponse` | `Response(mimetype="text/plain")` | `@Header` + 手动设置 |
| WebSocket | `@app.websocket` | `flask-socketio` | `@WebSocketGateway()` |
| 会话历史 | LangChain + Redis | 同库，无框架差异 | 同库，Service 注入 |
| 启动 | `uvicorn.run` | `flask run` / gunicorn | `NestFactory.create` + listen |

**结论**：`ai-server` 选 FastAPI 合理——Python AI 生态、async、OpenAPI 文档、WebSocket 原生支持，比 Flask 更现代，比 Django 更轻，比迁到 Java/TS 栈成本更低。
