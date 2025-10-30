from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from datetime import datetime
import sqlite3
import logging
import re
import os


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "exam2-secret"


# 路徑修改
def get_db_connection():
    conn = sqlite3.connect('shopping_data.db')
    if not os.path.exists('shopping_data.db'):
        logging.error(f"Database file not found at {'shopping_data.db'}")
        return None
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
@app.route('/page_register', methods=[])
def page_register():
    if request.method == 'POST':
        data = request.get_json()
       # 補齊空缺程式碼
        username = (data.get('username')).strip()
        password = (data.get('password')).strip()
        email = (data.get('email')).strip()
        if not username or not password or not email:
            return jsonify({"status": "error", "message": "此名稱已被使用"})

        if len(password) < 8:
            return jsonify({"status": "error", "message":"密碼字數不足8"})
        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password):
            return jsonify({"status": "error", "message":"密碼需包含英文字母大小寫"})
        
        if not re.compile(r"^[A-Za-z0-9._%+-]+@gmail\.com$").fullmatch(email):
            return jsonify({"status": "error", "message":"Email 格式不符重新輸入"})
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE users SET password=?, email=? WHERE id=?",
                        (password, email, row['id']))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": "帳號已存在，成功修改密碼或信箱"})
        cur.execute("INSERT INTO users (username, password, email) VALUES (?,?,?)",
                    (username, password, email))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "註冊成功"})
    return render_template('page_register.html')


def login_user(username, password):
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                return {"status": "success", "message": "Login successful"}
            else:
                return {"status": "error", "message": "Invalid username or password"}
        except sqlite3.Error as e:
            logging.error(f"Database query error: {e}")
            return {"status": "error", "message": "An error occurred"}
        finally:
            conn.close()
    else:
        return {"status": "error", "message": "Database connection error"}

@app.route('/page_login' , methods=['GET', 'POST'])
def page_login():
    try:
        if request.method == 'POST':
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            result = login_user(username, password)
            if result["status"] == "success":
                session['username'] = username
            return jsonify(result)
        return render_template('page_login_.html')
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 補齊剩餘副程式
@app.route('/index')
def index_page():
    if 'username' not in session:
        return redirect(url_for('page_login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('page_login'))

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.get_json()
    items = data.get('items')
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    cur = conn.cursor()
    for it in items:
        name = it.get('name')
        price = int(it.get('price', 0))
        qty = int(it.get('qty', 0))
        if not name or qty <= 0: 
            continue
        cur.execute("""INSERT INTO orders (Product, Price, Number, Total Price, Time)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (name, price, qty, price*qty, now_str))
    conn.commit()

    lines = [f"{now_str}，已成功下單：", ""]
    total_sum = 0
    for it in items:
        n = int(it.get('qty',0)); p = int(it.get('price',0)); name = it.get('name')
        if n>0 and name:
            total = n*p; total_sum += total
            lines.append(f"{name}: {p} NT/件 ×{n} 共 {total} NT")
    lines.append("")
    lines.append(f"此單花費總金額：{total_sum} NT")
    conn.close()

    return jsonify({"status":"success", "message":"\n".join(lines)})

# 補齊空缺程式碼
if __name__ == '__main__':
    app.run(debug=True)
    