import asyncpg
from asyncpg import Record
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_app import Application
from asyncpg.pool import Pool
from typing import Dict, List

routes = web.RouteTableDef()
DB_KEY = 'database'

async def create_database_pool(app: Application):
  print('Creating database pool')
  pool: Pool = await asyncpg.create_pool(host="127.0.0.1",
                                         port=5432,
                                         user='postgres',
                                         password='king',
                                         database='products',
                                         min_size=6,
                                         max_size=6)
  app[DB_KEY] = pool

async def destroy_database_pool(app: Application):
  print('Destroying database pool.')
  pool: Pool = app[DB_KEY]
  await pool.close()

@routes.get('/brands')
async def brands(request: Request) -> Response:
  connection: Pool = request.app[DB_KEY]
  brand_query = 'SELECT id, name FROM brand'
  results: List[Record] = await connection.fetch(brand_query)
  result_as_dict: list[Dict] = [dict(brand) for brand in results]
  return web.json_response(result_as_dict)

@routes.post('/product')
async def create_product(request):
  PRODUCT_NAME = 'product_name'
  BRAND_ID = 'brand_id'
  if not request.can_read_body:
    raise web.HTTPBadRequest()

  body = await request.json()

  if PRODUCT_NAME in body and BRAND_ID in body:
    db = request.app[DB_KEY]
    await db.execute('''
                     INSERT INTO product(id, name, brand_id) VALUES(DEFAULT, $1, $2)
                     ''',
                     body[PRODUCT_NAME], int(body[BRAND_ID]))
    return web.Response(status=201)
  else:
    raise web.HTTPBadRequest()

@routes.get('/products/{id}')
async def get_product(request: Request) -> Response:
  try:
    str_id = request.match_info['id']
    product_id = int(str_id)
    query = """
      SELECT id, name, brand_id FROM product WHERE id = $1
    """
    connection: Pool = request.app[DB_KEY]
    result: Record = await connection.fetchrow(query, product_id)

    if result is not None:
      return web.json_response(dict(result))
    else:
      raise web.HTTPNotFound()
  except ValueError:
    raise web.HTTPBadRequest()

app = web.Application()
app.on_startup.append(create_database_pool)
app.on_cleanup.append(destroy_database_pool)
app.add_routes(routes)

web.run_app(app)
