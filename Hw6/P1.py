import sqlite3
db_path = "ID_data.db"
Table = "ID_table"
col_ID = "ID"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

LETTER_CODE = {
    'A':10,'B':11,'C':12,'D':13,'E':14,'F':15,'G':16,'H':17,'I':34,
    'J':18,'K':19,'L':20,'M':21,'N':22,'O':35,'P':23,'Q':24,'R':25,
    'S':26,'T':27,'U':28,'V':29,'W':32,'X':30,'Y':31,'Z':33
}

def compute_check_digit(id9: str) -> int:
    s = id9.strip().upper()
    assert len(s) == 9 and s[0].isalpha() and s[1:].isdigit()

    code = LETTER_CODE[s[0]]
    X, Y = divmod(code, 10)
    weights = [8,7,6,5,4,3,2,1]
    nums = [int(ch) for ch in s[1:]]

    total = X*1 + Y*9 + sum(n*w for n, w in zip(nums, weights))
    d10 = (10 - (total % 10)) % 10
    return d10

def is_valid_id10(s: str) -> bool:
    s = s.strip().upper()
    if len(s) != 10: 
        return False
    if not (s[0].isalpha() and s[1:].isdigit()): 
        return False
    if s[1] not in "1289":                      
        return False
    code = LETTER_CODE.get(s[0])
    if code is None: 
        return False
    X, Y = divmod(code, 10)
    d = [int(ch) for ch in s[1:]]
    total = X*1 + Y*9 + d[0]*8 + d[1]*7 + d[2]*6 + d[3]*5 + d[4]*4 + d[5]*3 + d[6]*2 + d[7]*1 + d[8]*1
    return (total % 10) == 0

def describe_id(id_in: str) -> str:
    s = id_in.strip().upper()
    if len(s) == 9 and s[0].isalpha() and s[1:].isdigit():
        d10 = compute_check_digit(s)
        if d10 < 0:
            return "輸入錯誤，請重新輸入"
        s = s + str(d10)

    if not is_valid_id10(s):
        return "輸入錯誤，請重新輸入"

    cur.execute("SELECT county FROM County WHERE Alphabet = ?", (s[0],))
    row = cur.fetchone()
    county = row[0] if row else "未知"


    gender = {"1":"男性","2":"女性","8":"男性","9":"女性"}[s[1]]

    c3 = s[2]
    if c3 in "012345":
        category = "台灣出生之本籍國民"
    elif c3 == "6":
        category = "外國人"
    elif c3 == "7":
        category = "無國籍"
    elif c3 == "8":
        category = "港澳居民"
    elif c3 == "9":
        category = "大陸人士"
    else:
        category = "未知"

    return f"{s} {county} {gender} {category}"

while True:
    user_in = input("請輸入身分證字號(輸入 q 離開):").strip()
    if not user_in or user_in.lower() in {"q", "quit", "exit"}:
        print("結束查詢。")
        break
    print(describe_id(user_in))