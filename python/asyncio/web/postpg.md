# Postgres

```bash
\l # 查看数据库列表
\c dbName  # 选择数据库
\d # 查看表列表
\d tableName # 查看表信息
docker run --name king-postgres -e POSTGRES_PASSWORD=king -d postgres
docker run -d --name king-postgres -p 5432:5432 -e POSTGRES_PASSWORD=king -e PGDATA=/var/lib/postgresql/data/pgdata -v /Users/dreamerking/data/postgresql/data:/var/lib/postgresql/data
docker network ls
docker network create king
docker network connect king cd0acca7a530
docker run -it --rm --network king postgres psql -h king-postgres -U postgres
```

```bash
gunicorn -w 8 flask_01:app
```

n 请求数量
c 并发量

```bash
ab -V
ab -c 100 -n 500 -r [URL]
```

```bash
conda install gunicorn
gunicorn wsgi:application
curl localhost:8000
```

```bash
conda install uvicorn
uvicorn asgi:application
```
