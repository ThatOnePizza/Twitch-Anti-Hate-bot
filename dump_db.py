import sqlite3
import os

db_path = os.getenv("DB_PATH")

if not os.path.isfile(db_path):
    print(f"[ ERR ] File {db_path} doesn't exist")
    exit(-1)

with open("dump.txt", 'w') as f:
    con = sqlite3.connect(db_path)

    cur = con.cursor()

    bans_fetch = cur.execute('SELECT nickname FROM bans').fetchall()
    nicknames = [row[0] for row in bans_fetch]

    for nickname in nicknames:
        f.write(f"{nickname}\n")
