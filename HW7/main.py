import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import mimetypes
import os
import traceback
import re

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "users.db"
PORT = 5000

os.chdir(ROOT)

def ensure_grades_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            name TEXT,
            student_id TEXT PRIMARY KEY,
            score TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_grades_sorted():
    ensure_grades_table()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, student_id, score FROM grades")
    rows = cur.fetchall()
    conn.close()

    def key_fn(r):
        _, sid, _ = r
        s = str(sid).strip()
        try:
            return (int(s), s)
        except:
            return (10**18, s)
    rows.sort(key=key_fn)
    return rows

def upsert_grade(name, sid, score):
    ensure_grades_table()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM grades WHERE student_id=?", (sid,))
    if cur.fetchone():
        cur.execute("UPDATE grades SET name=?, score=? WHERE student_id=?", (name, score, sid))
    else:
        cur.execute("INSERT INTO grades(name, student_id, score) VALUES(?,?,?)", (name, sid, score))
    conn.commit()
    conn.close()

def delete_grade(sid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM grades WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()

def inject_rows_into_grades_html(raw_html: str) -> str:
    trs = "\n".join(
        f"<tr><td>{name}</td><td>{sid}</td><td>{score}</td></tr>"
        for (name, sid, score) in get_grades_sorted()
    )
    pattern = r'(<tbody\s+id=["\']studentTable["\']\s*>)(.*?)(</tbody>)'
    return re.sub(pattern, r'\1' + trs + r'\3', raw_html, flags=re.DOTALL | re.IGNORECASE)

def safe_read(relurl: str):
    p = (ROOT / relurl.lstrip("/")).resolve()
    if ROOT not in p.parents and p != ROOT / relurl.lstrip("/"):
        raise FileNotFoundError(relurl)
    with open(p, "rb") as f:
        return p, f.read()

class SimpleHandler(BaseHTTPRequestHandler):
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
            return "/static/favicon.ico"
        if low.startswith("/templates/") or low.startswith("/static/"):
            return path
        return path

    # ---------- FIXED GET ----------
    def do_GET(self):
        try:
            # 1) 先處理 /Grades.html：讀檔→注入資料→一次回應（不要二次送 header）
            if self.path.split("?", 1)[0].lower() == "/grades.html":
                p = ROOT / "templates" / "Grades.html"
                if not p.exists():
                    self._send_error(404, "File not found")
                    return
                raw = p.read_text(encoding="utf-8")
                merged = inject_rows_into_grades_html(raw)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(merged.encode("utf-8"))
                return

            # 2) 其餘當作靜態檔回傳
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

    # ---------- FIXED POST ----------
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            params = urllib.parse.parse_qs(body)
            path = self.path.lower()

            # /login
            if path == "/login":
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
                    self._html_msg("密碼錯誤，請重新輸入。")
                else:
                    self._html_msg("查無此帳號。")
                return

            # /grades/add
            if path == "/grades/add":
                teacher = urllib.parse.unquote(params.get("teacher", [""])[0])
                name = params.get("student_name", [""])[0].strip()
                sid  = params.get("student_id", [""])[0].strip()
                score= params.get("student_score", [""])[0].strip()
                if name and sid and score:
                    upsert_grade(name, sid, score)
                self.send_response(302)
                self.send_header("Location", f"/Grades.html?teacher={urllib.parse.quote(teacher)}")
                self.end_headers()
                return

            # /grades/delete
            if path == "/grades/delete":
                teacher = urllib.parse.unquote(params.get("teacher", [""])[0])
                sid_del = params.get("student_id_del", [""])[0].strip()
                if sid_del:
                    delete_grade(sid_del)
                self.send_response(302)
                self.send_header("Location", f"/Grades.html?teacher={urllib.parse.quote(teacher)}")
                self.end_headers()
                return

            # 其他 POST
            self._send_error(404, "Unknown POST endpoint")
        except Exception:
            print("[POST 500] Unexpected error")
            traceback.print_exc()
            self._send_error(500, "Internal Server Error")

    # ---------- helpers ----------
    def _send_error(self, code: int, msg: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(f"{code} {msg}".encode("utf-8"))

    def _html_msg(self, text: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        html = f"<h2>{text}</h2><a href='/Login.html'>返回登入頁面</a>"
        self.wfile.write(html.encode("utf-8"))

    def check_login(self, username, password):
        print(f"[DB] using: {DB_PATH}  exists={DB_PATH.exists()}")
        if not DB_PATH.exists():
            return "no_user", None
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT password FROM teachers WHERE username=? LIMIT 1", (username,))
            row = cur.fetchone()
            if not row:
                try:
                    cur.execute("SELECT username FROM teachers")
                    all_users = [r[0] for r in cur.fetchall()]
                    print(f"[DB] usernames in teachers: {all_users}")
                except Exception:
                    pass
                conn.close()
                return "no_user", None
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
