import sqlite3

DB_PATH = "bot_data.db"

# Initialize DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS banned (
                user_id INTEGER PRIMARY KEY
            )""")
conn.commit()
conn.close()


# ------------------------
# Users
# ------------------------
async def add_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
    conn.commit()
    conn.close()

async def remove_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

async def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users


# ------------------------
# Ban
# ------------------------
async def ban_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO banned(user_id) VALUES(?)", (user_id,))
    conn.commit()
    conn.close()

async def unban_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM banned WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

async def is_banned(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM banned WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return bool(result)
