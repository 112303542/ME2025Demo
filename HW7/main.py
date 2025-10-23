import sqlite3 
db_path = "users.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

