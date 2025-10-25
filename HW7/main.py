import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import mimetypes

Root = Path(__file__).resolve().parent
db_path = "users.db"
PORT = 8000
conn = sqlite3.connect(db_path)
cur = conn.cursor()

def safe_open(relpath: str):
    p = (Root / relpath.lstrip("/")).resolve()
    if Root in p.parents or p == Root / relpath.lstrip("/"):
        return p.open("rb")
    raise FileNotFoundError

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/templates/Login.html"
        elif path == "/Login.html":
            path = "/templates/Login.html"
        elif path == "/Grades.html":
            path = "/templates/Grades.html"

        try:
            with safe_open(path) as f:
                self.send_response(200)
                ctype = mimetypes.guess_type(path)[0] or "text/plain"
                if ctype.startswith(("text/", "application/javascript", "application/json")) and "charset" not in ctype:
                    ctype += "; charset=utf-8"
                self.send_header("Content-Type", ctype)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")
            params = urllib.parse.parse_qs(body)

            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]

            status, teacher_name = self.check_login(username, password)

            if status == "ok":
                encoded_name = urllib.parse.quote(teacher_name)
                self.send_response(302)
                self.send_header("Location", f"/Grades.html?teacher={encoded_name}")
                self.end_headers()
            elif status == "wrong_password":
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<h2>密碼錯誤，請重新輸入。</h2><a href='/Login.html'>返回登入頁面</a>")

            elif status == "no_user":
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<h2>查無此帳號。</h2><a href='/Login.html'>返回登入頁面</a>")
    
    def _msg(self, text):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = f"<h2>{text}</h2><a href='/Login.html'>返回登入頁面</a>"
        self.wfile.write(html.encode("utf-8"))

    def check_login(self, username, password):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT username FROM teachers WHERE username=? AND password=?", (username, password))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
    

if __name__ == "__main__":
    server = HTTPServer(("", PORT), SimpleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()