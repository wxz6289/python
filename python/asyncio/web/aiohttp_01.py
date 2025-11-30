from typing import Any
from aiohttp import web
from datetime import datetime
from aiohttp.web_request import Request
from aiohttp.web_response import Response

routes = web.RouteTableDef()

@routes.get('/time')
async def time(request: Request) -> Response:
  today = datetime.today()
  result = {
    'mouth': today.month,
    'day': today.day,
    'time': str(today.time())
  }
  return web.json_response(result)

@routes.get('/')
async def get_data(request: Request) -> Response:
  shared_data = request.app['share_data']
  return web.json_response(shared_data)

async def init(app):
  app['share_data'] = {
    'name': 'king'
  }

app = web.Application()
app.on_startup.append(init)
app.add_routes(routes)

web.run_app(app)
