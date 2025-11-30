from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)
conn_info = "dbname=products user=postgres password=king host=127.0.0.1"
db = psycopg2.connect(conn_info)

@app.route('/brands')
def brands():
  cur = db.cursor()
  cur.execute('SELECT id, name FROM brand')
  rows = cur.fetchall()
  cur.close()
  return jsonify([{ 'id': id, 'name': name} for [id, name] in rows])
