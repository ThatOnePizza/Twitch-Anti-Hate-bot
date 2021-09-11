import sqlite3
import sys
import os

db_path = os.getenv("DB_PATH")

if len(sys.argv) < 2:
    print(f"Missing argument file name.\n{sys.argv[0]} ban_list.txt", file=sys.stderr)
    exit(-1)

if not os.path.isfile(db_path):
    print(f"[ WARN ] File {db_path} doesn't exist, creating a new one")

con = sqlite3.connect(db_path)

cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS bans
               (nickname TEXT UNIQUE)''')


with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        try:
            cur.execute("INSERT INTO bans VALUES (?)", (line.strip(),))
            print(f"Added {line.strip()}")
        except sqlite3.IntegrityError as e:
            print(f"[Exception] {e} | {line.strip()}")

con.commit()

con.close()