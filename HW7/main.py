import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import mimetypes
import os
import re

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "users.db"
PORT = 5000

os.chdir(ROOT)

# ---------- DB helpers ----------
def ensure_grades_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                name TEXT,
                student_id TEXT PRIMARY KEY,
                score TEXT
            )
        """)

def get_grades_sorted():
    """[(name, student_id, score)] 依學號遞增排序（能轉數字就用數字排）"""
    ensure_grades_table()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT name, student_id, score FROM grades").fetchall()

    def key_fn(r):
        sid = str(r[1]).strip()
        try:
            return (int(sid), sid)
        except:
            return (10**18, sid)
    rows.sort(key=key_fn)
    return rows

def upsert_grade(name, sid, score):
    ensure_grades_table()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT 1 FROM grades WHERE student_id=?", (sid,))
        if cur.fetchone():
            conn.execute("UPDATE grades SET name=?, score=? WHERE student_id=?", (name, score, sid))
        else:
            conn.execute("INSERT INTO grades(name, student_id, score) VALUES(?,?,?)", (name, sid, score))

def delete_grade(sid):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM grades WHERE student_id=?", (sid,))

def inject_rows_into_grades_html(raw_html: str) -> str:
    trs = "\n".join(
        f"<tr><td>{n}</td><td>{sid}</td><td>{sc}</td></tr>"
        for (n, sid, sc) in get_grades_sorted()
    )
    # 用表格資料覆蓋 <tbody id="studentTable"> ... </tbody>
    pattern = r'(<tbody\s+id=["\']studentTable["\']\s*>)(.*?)(</tbody>)'
    return re.sub(pattern, r'\1' + trs + r'\3', raw_html, flags=re.DOTALL | re.IGNORECASE)

def safe_read(relurl: str):
    p = (ROOT / relurl.lstrip("/")).resolve()
    if ROOT not in p.parents and p != ROOT / relurl.lstrip("/"):
        raise FileNotFoundError(relurl)
    with open(p, "rb") as f:
        return p, f.read()

# ---------- HTTP handler ----------
class SimpleHandler(BaseHTTPRequestHandler):
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

    def do_GET(self):
        try:
            # /Grades.html：先把 DB 資料注入表格再回應
            if self.path.split("?", 1)[0].lower() == "/grades.html":
                p = ROOT / "templates" / "Grades.html"
                if not p.exists():
                    return self._send_error(404, "File not found")
                merged = inject_rows_into_grades_html(p.read_text(encoding="utf-8"))
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(merged.encode("utf-8"))
                return

            # 其他靜態檔
            rel = self._map(self.path)
            file_path, data = safe_read(rel)
            ctype = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            if file_path.suffix in {".html", ".js", ".css"} and "charset" not in ctype:
                ctype += "; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self._send_error(404, "File not found")

    def do_POST(self):
        # 讀取表單
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        params = urllib.parse.parse_qs(body)
        path = self.path.lower()

        # ---------- /login ----------
        if path == "/login":
            username = params.get("username", [""])[0].strip()
            password = params.get("password", [""])[0].strip()

            login_status, teacher_name = self.check_login(username, password)

            if login_status == "ok":
                encoded = urllib.parse.quote(teacher_name)
                self.send_response(302)
                self.send_header("Location", f"/Grades.html?teacher={encoded}")
                self.end_headers()
            elif login_status == "wrong_password":
            # 若你有在 Login.html 依 ?err=pwd 顯示 alert，這樣導回就行
                self.send_response(302)
                self.send_header("Location", "/Login.html?err=pwd")
                self.end_headers()
            else:  # "no_user"
                self.send_response(302)
                self.send_header("Location", "/Login.html?err=user")
                self.end_headers()
            return

        # ---------- /grades/add ----------
        if path == "/grades/add":
            teacher = urllib.parse.unquote(params.get("teacher", [""])[0])
            name = params.get("student_name", [""])[0].strip()
            sid = params.get("student_id", [""])[0].strip()
            score = params.get("student_score", [""])[0].strip()
            if name and sid and score:
                upsert_grade(name, sid, score)
            self._redirect_grades(teacher)
            return

        # ---------- /grades/delete ----------
        if path == "/grades/delete":
            teacher = urllib.parse.unquote(params.get("teacher", [""])[0])
            sid_del = params.get("student_id_del", [""])[0].strip()
            if sid_del:
                delete_grade(sid_del)
            self._redirect_grades(teacher)
            return

        # 其他未知端點
        self._send_error(404, "Unknown POST endpoint")

    # ---------- helpers ----------
    def _redirect_grades(self, teacher):
        encoded = urllib.parse.quote(teacher or "")
        self.send_response(302)
        self.send_header("Location", f"/Grades.html?teacher={encoded}")
        self.end_headers()

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
        self.wfile.write(f"<h2>{text}</h2><a href='/Login.html'>返回登入頁面</a>".encode("utf-8"))

    def check_login(self, username, password):
        if not DB_PATH.exists():
            return "no_user", None
        try:
            with sqlite3.connect(DB_PATH) as conn:
                row = conn.execute(
                    "SELECT password FROM teachers WHERE username=? LIMIT 1",
                    (username,)
                ).fetchone()
            if not row:
                return "no_user", None
            return ("ok", username) if str(password).strip() == str(row[0]).strip() else ("wrong_password", None)
        except Exception:
            # 發生任何 DB 錯誤時就當查無帳號
            return "no_user", None

if __name__ == "__main__":
    print(f"URL:  http://127.0.0.1:{PORT}/Login.html")
    server = HTTPServer(("", PORT), SimpleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
