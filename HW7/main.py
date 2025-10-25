import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import mimetypes
import os
import traceback

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "users.db"
PORT = 5000  # 你說 5000 可用

os.chdir(ROOT)  # 確保相對路徑正確

def safe_read(relurl: str):
    p = (ROOT / relurl.lstrip("/")).resolve()
    if ROOT not in p.parents and p != ROOT / relurl.lstrip("/"):
        raise FileNotFoundError(relurl)
    with open(p, "rb") as f:
        return p, f.read()

class SimpleHandler(BaseHTTPRequestHandler):
    # 方便觀察請求
    def log_message(self, fmt, *args):
        print(f"[HTTP] {self.address_string()} - {self.command} {self.path}")

    def _map(self, url: str) -> str:
        path = url.split("?", 1)[0]
        low = path.lower()

        if low in {"/", "/login.html"}:
            return "/templates/Login.html"
        if low == "/grades.html":
            return "/templates/Grades.html"
        if low == "/favicon.ico":
            return "/static/favicon.ico"  # 沒有也會 404（正常）
        if low.startswith("/templates/") or low.startswith("/static/"):
            return path
        return path

    def do_GET(self):
        try:
            rel = self._map(self.path)
            file_path, data = safe_read(rel)
            ctype = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            if file_path.suffix in {".html", ".js", ".css"} and "charset" not in ctype:
                ctype += "; charset=utf-8"
            print(f"[GET 200] {self.path} -> {file_path}")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            print(f"[GET 404] {self.path} (mapped to {rel})")
            self._send_error(404, "File not found")
        except Exception:
            print("[GET 500] Unexpected error")
            traceback.print_exc()
            self._send_error(500, "Internal Server Error")

    def do_POST(self):
        try:
            if self.path.lower() != "/login":
                self._send_error(404, "Unknown POST endpoint")
                return

            length = int(self.headers.get("Content-Length", "0") or 0)
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            params = urllib.parse.parse_qs(body)

            # ★ 1) 去除前後空白，避免空白/換行造成比對失敗
            username = params.get("username", [""])[0].strip()
            password = params.get("password", [""])[0].strip()
            print(f"[LOGIN] username={username!r}")

            status, teacher_name = self.check_login(username, password)

            if status == "ok":
                encoded = urllib.parse.quote(teacher_name)
                self.send_response(302)
                self.send_header("Location", f"/Grades.html?teacher={encoded}")
                self.send_header("Connection", "close")
                self.end_headers()
            elif status == "wrong_password":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Connection", "close")
                self.end_headers()
                html = "<h2>密碼錯誤，請重新輸入。</h2><a href='/Login.html'>返回登入頁面</a>"
                self.wfile.write(html.encode("utf-8"))
            else:  # no_user
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Connection", "close")
                self.end_headers()
                html = "<h2>查無此帳號。</h2><a href='/Login.html'>返回登入頁面</a>"
                self.wfile.write(html.encode("utf-8"))
        except Exception:
            print("[POST 500] Unexpected error")
            traceback.print_exc()
            self._send_error(500, "Internal Server Error")

    # === 工具方法 ===
    def _send_error(self, code: int, msg: str):
        # 統一送錯誤，避免出現「未傳送任何數據」
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(f"{code} {msg}".encode("utf-8"))

    def check_login(self, username, password):
        """
        回傳: ('ok', name) | ('wrong_password', None) | ('no_user', None)
        目前用 username 當顯示名稱；若 teachers 有 name 欄位，改成 SELECT name,password 並回傳 name。
        """
        # ★ 2) 印出實際使用的 DB 路徑，確認沒有打到錯 DB
        print(f"[DB] using: {DB_PATH}  exists={DB_PATH.exists()}")

        if not DB_PATH.exists():
            return "no_user", None

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # 先檢查帳號是否存在
            cur.execute("SELECT password FROM teachers WHERE username=? LIMIT 1", (username,))
            row = cur.fetchone()

            if not row:
                # ★ 3) 額外列出 DB 內所有帳號，幫你確認帳號是否拼錯/資料是否在這個 DB
                try:
                    cur.execute("SELECT username FROM teachers")
                    all_users = [r[0] for r in cur.fetchall()]
                    print(f"[DB] usernames in teachers: {all_users}")
                except Exception as e:
                    print("[DB] cannot list usernames:", e)

                conn.close()
                return "no_user", None

            # ★ 4) 型別與空白一致化：把 DB 的密碼轉字串並 strip 後再比
            db_pw = str(row[0]).strip()
            if str(password).strip() != db_pw:
                conn.close()
                return "wrong_password", None

            conn.close()
            return "ok", username

        except Exception:
            traceback.print_exc()
            return "no_user", None

if __name__ == "__main__":
    print("=== Server Info ===")
    print(f"ROOT: {ROOT}")
    print(f"DB:   {DB_PATH}  ({'存在' if DB_PATH.exists() else '不存在'})")
    print(f"URL:  http://127.0.0.1:{PORT}/Login.html")
    print("===================")
    server = HTTPServer(("", PORT), SimpleHandler)
    print("按 Ctrl + C 可停止伺服器。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 已關閉伺服器。")
        server.server_close()
