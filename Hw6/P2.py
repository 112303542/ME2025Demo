import sqlite3
import re
db_path = "users.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

def is_valid_email(email: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", email) is not None

def password_violations(pw: str):
    v = []
    if len(pw) < 8:
        v.append("長度不足 8 個字元")
    if not re.search(r"[A-Z]", pw):
        v.append("需包含至少一個大寫英文字母 (A-Z)")
    if not re.search(r"[a-z]", pw):
        v.append("需包含至少一個小寫英文字母 (a-z)")
    if not re.search(r"[0-9]", pw):
        v.append("需包含至少一個數字 (0-9)")
    if not re.search(r"[^A-Za-z0-9]", pw):
        v.append("需包含至少一個特殊字元（如 !@#$% 等）")
    return (len(v) == 0), v

def sign_up():
    name = input("Name:").strip()
    if not name:
        print("姓名不可為空")
        return
    
    while True:
        email = input("Email(須為xxx@gmail.com):").strip()
        if is_valid_email(email):
            break
        print("Email 格式不符，請重新輸入")
    
    while True:
        pw = input("Password(至少8碼,含大小寫、數字、特殊字元):")
        ok, violations = password_violations(pw)
        if ok:
            break
        else:
            print("密碼不符合以下規則：")
            for i, msg in enumerate(violations, start=1):
                print(f"  {i}. {msg}")
            print("請重新輸入。\n")
    
    ans = input(f"save {name} | {email} | {pw} | Y / N ? (Y更新/儲存資料,N返回進入模式畫面) ").strip().lower()
    if ans != "y":
        return

    cur.execute("SELECT 1 FROM user_data WHERE email=?", (email,))
    exists = cur.fetchone() is not None
    
    if not exists:
        cur.execute("INSERT INTO user_data (name, email, password) VALUES (?, ?, ?)",(name, email, pw))
        conn.commit()
        print("註冊完成（已新增資料）。")
    else:
        print("該 Email 已存在。是否更新此 Email 資訊 ?")
        confirm = input("Y / N ? ").strip().lower()
        if confirm == "y":
            cur.execute("UPDATE user_data SET name=?, password=? WHERE email=?",(name, pw, email))
            conn.commit()
            print("資料已更新完成。")
        else:
            print("未更新，返回模式畫面。")

def sign_in():
    name = input("Name:").strip()
    email = input("Email:").strip()

    cur.execute("SELECT password FROM user_data WHERE name=? AND email=?", (name, email))
    row = cur.fetchone()
    if not row:
        print("姓名或 Email 錯誤。")
        return

    correct_pw = row[0]
    max_try = 5
    for i in range(max_try):
        pw = input(f"Password(剩餘 {max_try - i} 次 ; 按 q 返回):")
        if pw.lower() in {"q","quit","exit"}:
            print("已返回主選單。")
            return
        if pw == correct_pw:
            print("登入成功！")
            return
        ans = input("密碼錯誤，是否忘記密碼？(Y/N):").strip().lower()
        if ans == "y":
            print("請重新註冊以更新密碼。")
            sign_up()
            return
    print("已超過最大重試次數。")

def main():
    while True:
        mode = input("\n請選擇模式:(a) sign up / (b) sign in / (q) 離開：").strip().lower()
        if mode == "a":
            sign_up()
        elif mode == "b":
            sign_in()
        elif mode == "q":
            print("系統結束，再見！")
            break
        else:
            print("請輸入 a 或 b")

if __name__ == "__main__":
    try:
        main()
    finally:
        conn.close()