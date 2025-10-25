import sqlite3 
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

db_path = "users.db"
PORT = 8000
conn = sqlite3.connect(db_path)
cur = conn.cursor()

Table_name = "teachers"
cur.execute(f"PRAGMA table_info({Table_name})")
columns = [col[1] for col in cur.fetchall()]

cur.execute(f"SELECT * FROM {Table_name}")
rows = cur.fetchall()
conn.close()

data = [dict(zip(columns, row)) for row in rows]
json_file = "json.js"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
