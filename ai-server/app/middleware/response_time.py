from fastapi import Request, Response
import time
from datetime import datetime, timezone

async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print(f"Request: {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Response: {response.headers}")
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Response-Time"] = str(process_time)
    response.headers["X-Response-DateTime"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return response
