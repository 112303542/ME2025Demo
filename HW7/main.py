import sqlite3 
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

db_path = "users.db"
PORT = 8000
conn = sqlite3.connect(db_path)
cur = conn.cursor()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/Login.html"
        try:
            with open(self.path.strip("/"), "rb") as f:
                self.send_response(200)
                if self.path.endswith(".html"):
                    self.send_header("Content-type", "text/html; charset=utf-8")
                elif self.path.endswith(".js"):
                    self.send_header("Content-type", "application/javascript; charset=utf-8")
                else:
                    self.send_header("Content-type", "text/plain; charset=utf-8")
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

            if teacher_name:
                encoded_name = urllib.parse.quote(teacher_name)
                self.send_response(302)
                self.send_header("Location", f"/Grades.html?teacher={encoded_name}")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<h2>帳號或密碼錯誤</h2><a href='/Login.html'>返回登入頁面</a>")

