from enum import Enum
from pathlib import Path as FilePath
from typing import Annotated, Any, Self
import uuid
from pathlib import Path as PathLibPath

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Path,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
)
from pydantic import (
    UUID4,
    BaseModel,
    BeforeValidator,
    Field,
    GetCoreSchemaHandler,
    WithJsonSchema,
    field_validator,
)
from asyncio import gather, sleep
import time
import aiofiles

from pydantic_core import CoreSchema, core_schema

router = APIRouter(prefix="/path", tags=["path"])

UPLOAD_DIR = FilePath(__file__).resolve().parents[2] / "resources"
PDF_FILENAME = "keyboard-shortcuts-macos.pdf"
CHUNK_SIZE = 1024 * 1024
BinaryUploadFile = Annotated[
    UploadFile,
    WithJsonSchema({"type": "string", "format": "binary"}),
]


async def _save_upload_stream(
    file: UploadFile,
    *,
    fallback_name: str | None = None,
    used_names: set[str] | None = None,
) -> dict[str, Any]:
    safe_name = FilePath(file.filename or fallback_name or str(uuid.uuid4())).name
    dest = UPLOAD_DIR / safe_name
    if used_names is not None and dest.name in used_names:
        dest = UPLOAD_DIR / f"{dest.stem}_{uuid.uuid4().hex[:8]}{dest.suffix}"
    if used_names is not None:
        used_names.add(dest.name)
    size = 0
    try:
        async with aiofiles.open(dest, "wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                await out.write(chunk)
    finally:
        await file.close()
    return {
        "file_name": dest.name,
        "size": size,
        "content_type": file.content_type,
    }


class ModelName(str, Enum):
    deepseek = "deepseek-v4-flash"
    chatgpt = "chatgpt5.5"
    qwen = "qwen3.5"
    claude = "claude4.6"


class PagePattern(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )

    @classmethod
    def validate(cls, value: str) -> Self:
        if not value.startswith("p"):
            raise ValueError(f"Invalid page pattern {value}")
        return cls(value)


@router.get("/item/{id}")
async def get_path(id: int = Path(..., gt=20, le=100)):
    return {"id": id}


@router.post("/item0/{id}")
async def get_path1(id: str = Path(..., pattern=r"^[a-z]+\d$")):
    return {"id": id}


@router.get("/model/{name}")
async def get_model(name: ModelName):
    return {"model_name": name.value}


@router.get("/page/{page}")
async def get_page(page: PagePattern):
    return {"page": page}


def validate_page(page: str) -> str:
    if not page.startswith("p"):
        raise ValueError(f"Invalid page pattern {page}")
    return page


PagePattern2 = Annotated[str, BeforeValidator(validate_page)]


@router.get("/page2/{page}")
async def get_page2(page: PagePattern2):
    return {"page": page}


class User(BaseModel):
    id: int
    email: str
    name: str = Field(
        min_length=2, max_length=20, title="名称", description="User name"
    )
    age: int = Field(
        ge=18, le=100, default=26, title="User age", description="User age"
    )

    @field_validator("email")
    def validate_email(cls, email: str) -> str:
        if not email.endswith("@gmail.com"):
            raise ValueError("Email must end with @gmail.com")
        return email


@router.get("/user/{user_id}")
async def get_user(user_id: int) -> User:
    return User(id=user_id, email="king@gmail.com", name="King", age=26)


@router.get("/redrect")
async def redrect(user_id: int, q: str):
    return RedirectResponse(url=f"/path/user/{user_id}?q={q}")


@router.post("/user")
async def create_user(user: User) -> User:
    return user


class Order(BaseModel):
    items: list[str] = Field(..., min_length=1, description="Items in the order")
    address: str = Field(..., description="Address of the order")


@router.post("/order")
async def create_order(order: Order) -> Order:
    return order


@router.post("/order2")
async def create_order2(order: Annotated[Order, Form(...)]):
    return order


@router.patch("/order/{id}")
async def update_order(id: int, items: list[str] = Form(...)) -> Order:
    return Order(items=items, address="Beijing")


@router.get("/async")
async def async_test():
    start = time.time()
    task = [sleep(1) for _ in range(10)]
    await gather(*task)
    return {"time": time.time() - start, "tasks": len(task)}


@router.get("/sync")
def sync_test():
    start = time.time()
    for _ in range(10):
        time.sleep(1)
    return {"time": time.time() - start, "tasks": 10}


@router.post("/file")
async def upload_file(file_name: str = Form(...), file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = FilePath(file.filename or file_name).name
    content = await file.read()
    (UPLOAD_DIR / safe_name).write_bytes(content)
    return {
        "file_name": safe_name,
        "size": len(content),
        "content_type": file.content_type,
    }


@router.post("/file3")
async def upload_file3(file_name: str = Form(...), file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if file.filename is not None:
        extension = PathLibPath(file.filename).suffix
        print("=" * 10, extension, "=" * 10)
    return await _save_upload_stream(file, fallback_name=file_name)


@router.post("/batch")
async def upload_batch(files: Annotated[list[BinaryUploadFile], File()]):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    used_names: set[str] = set()
    for file in files:
        results.append(await _save_upload_stream(file, used_names=used_names))
    return results


@router.get("/client")
async def client_info(request: Request):
    return {
        "client": request.client,
        "headers": request.headers,
        "cookies": request.cookies,
        "query_params": request.query_params,
        "path_params": request.path_params,
        "body": request.body,
        "url": request.url,
        "method": request.method,
        "ua": request.headers.get("user-agent"),
        "ip": request.headers.get("x-forwarded-for"),
        "port": request.headers.get("x-forwarded-port"),
        "host": request.headers.get("host"),
        "scheme": request.headers.get("x-forwarded-scheme"),
        "path": request.headers.get("x-forwarded-path"),
        "query": request.headers.get("x-forwarded-query"),
        "fragment": request.headers.get("x-forwarded-fragment"),
        "accept": request.headers.get("accept"),
        "accept-encoding": request.headers.get("accept-encoding"),
        "accept-language": request.headers.get("accept-language"),
    }


@router.get("/download")
async def download_file():
    return Response(
        content="Hello, World!",
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=hello.txt"},
    )


@router.get("/download/pdf")
async def download_pdf_file():
    pdf_path = UPLOAD_DIR / PDF_FILENAME
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {PDF_FILENAME}")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=PDF_FILENAME,
    )


async def generate_chunk(file_path: PathLibPath, chunk_size: int = 1024 * 1024):
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(chunk_size):
            yield bytes(chunk)


@router.get("/download/pdf/stream")
async def download_pdf_file_stream():
    file_path = UPLOAD_DIR / PDF_FILENAME
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    return StreamingResponse(
        generate_chunk(file_path),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={PDF_FILENAME}"},
    )


@router.get("/response/html")
async def response_html():
    return HTMLResponse(content="<h1>Hello, World!</h1>")


@router.get("/response/html2", response_class=HTMLResponse)
async def response_html2():
    return "<h1>Hello, World2!</h1>"


@router.get("/response/redirect", status_code=status.HTTP_302_FOUND)
async def response_redirect():
    return RedirectResponse(url="/path/response/html")
