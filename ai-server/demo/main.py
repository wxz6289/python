from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello, World!"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str) -> dict[str, str]:
    return {"file_path": file_path}

if __name__ == "__main__":
    from uvicorn import run
    run(app, host="127.0.0.1", port=8000)
