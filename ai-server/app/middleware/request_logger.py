from fastapi import Request


def request_logger(request: Request):
    print(request.method, request.url)
    return None
