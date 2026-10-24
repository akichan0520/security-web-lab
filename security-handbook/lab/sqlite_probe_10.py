#!/usr/bin/env python3
"""ローカル専用のSQLite SQLi教材。ネット接続・サーバ起動・ファイル読取なし。

Usage:
  python3 security-handbook/lab/sqlite_probe_10.py
  python3 security-handbook/lab/sqlite_probe_10.py "Travel Kit'"
  python3 security-handbook/lab/sqlite_probe_10.py "NoSuch' UNION SELECT NULL,(SELECT label FROM practice_records LIMIT 1) --"

重要: SQL文字列連結は脆弱な例を意図して再現するためだけに使う。
"""
import sqlite3
import sys


def prepare_db():
    db = sqlite3.connect(":memory:")
    db.executescript("""
    CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, is_active INTEGER, campaign TEXT);
    CREATE TABLE practice_records (id INTEGER PRIMARY KEY, label TEXT);
    INSERT INTO products VALUES (1,'Alpha',1,'demo'),(2,'Omega',1,'demo'),(3,'Travel Kit',1,'demo');
    INSERT INTO practice_records VALUES (1,'CTF{PRACTICE_ONLY}');
    """)
    return db


def run(db, value):
    unsafe_sql = "SELECT id,name FROM products WHERE name='" + value + "'"
    print("\n[1] 入力:", repr(value))
    print("[2] 脆弱なSQL:", unsafe_sql)
    try:
        unsafe_result = db.execute(unsafe_sql).fetchall()
        print("[3] 脆弱なSQLの結果:", unsafe_result)
    except sqlite3.Error as e:
        print("[3] 脆弱なSQLのエラー:", type(e).__name__, str(e))
    print("[4] パラメータ化して同じ入力を送信:")
    safe_sql = "SELECT id,name FROM products WHERE name=?"
    try:
        safe_result = db.execute(safe_sql, (value,)).fetchall()
        print("    SQL:", safe_sql)
        print("    結果:", safe_result)
    except sqlite3.Error as e:
        print("    安全なSQLでのエラー:", e)


def main():
    db = prepare_db()
    if len(sys.argv) > 1:
        run(db, sys.argv[1]); return
    for s in [
        "Travel Kit",
        "Travel Kit'",
        "Travel Kit' AND 1=1 --",
        "Travel Kit' AND 1=2 --",
        "NoSuch' UNION SELECT NULL,sqlite_version() --",
        "NoSuch' UNION SELECT NULL,(SELECT name FROM sqlite_schema WHERE type='table' AND name='practice_records') --",
        "NoSuch' UNION SELECT NULL,(SELECT name FROM pragma_table_info('practice_records') ORDER BY cid LIMIT 1 OFFSET 1) --",
        "NoSuch' UNION SELECT NULL,(SELECT label FROM practice_records LIMIT 1) --",
    ]:
        run(db, s)

if __name__ == "__main__":
    main()
