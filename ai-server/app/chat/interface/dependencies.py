from fastapi import Depends, Request

from app.chat.infrastructure.master import Master
from app.config import get_settings


def get_master(request: Request) -> Master:
    master = request.app.state.master
    if master is None:
        master = Master(get_settings())
        request.app.state.master = master
    return master
