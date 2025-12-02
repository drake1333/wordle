import sqlite3
from config import DB_FILE
from datetime import date

def get_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                      username TEXT PRIMARY KEY,
                      password TEXT)""")
    conn.commit()
    return conn, cursor

def ensure_statistics_table():
    conn, cursor = get_db()
    cursor.execute("""CREATE TABLE IF NOT EXISTS statistics (
                      username TEXT PRIMARY KEY,
                      wins INTEGER DEFAULT 0,
                      losses INTEGER DEFAULT 0,
                      last_daily_play TEXT
                      )""")
    conn.commit()
    cursor.execute("PRAGMA table_info(statistics)")
    cols = [r[1] for r in cursor.fetchall()]
    if "last_daily_play" not in cols:
        try:
            cursor.execute("ALTER TABLE statistics ADD COLUMN last_daily_play TEXT")
            conn.commit()
        except Exception:
            pass
    conn.close()

def update_stats_db(username, win: bool, set_last_daily_play=False):
    if not username:
        return False
    conn, cursor = get_db()
    
   
    cursor.execute("SELECT wins, losses FROM statistics WHERE username=?", (username,))
    row = cursor.fetchone()
    
    if row:
        if win:
            cursor.execute("UPDATE statistics SET wins = wins + 1 WHERE username=?", (username,))
        else:
            cursor.execute("UPDATE statistics SET losses = losses + 1 WHERE username=?", (username,))
    else:
        # Create row if it doesn't exist
        wins = 1 if win else 0
        losses = 0 if win else 1
        cursor.execute("INSERT INTO statistics (username, wins, losses) VALUES (?, ?, ?)",
                       (username, wins, losses))
        
    if set_last_daily_play:
        today = date.today().isoformat()
        cursor.execute("UPDATE statistics SET last_daily_play = ? WHERE username = ?", (today, username))
        
    conn.commit()
    conn.close()
    return True

def get_user_stats(username):
    if not username:
        return {"wins":0,"losses":0,"last_daily_play":None}
    conn, cursor = get_db()
    cursor.execute("SELECT wins, losses, last_daily_play FROM statistics WHERE username=?", (username,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return {"wins": r[0] or 0, "losses": r[1] or 0, "last_daily_play": r[2]}
    return {"wins":0,"losses":0,"last_daily_play":None}

def can_play_daily(username):
    if not username:
        return False
    stats = get_user_stats(username)
    last = stats.get("last_daily_play")
    return last != date.today().isoformat()

def register_user(username, password):
    conn, cursor = get_db()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        cursor.execute("INSERT OR IGNORE INTO statistics (username, wins, losses) VALUES (?, 0, 0)", (username,))
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def authenticate_user(username, password):
    conn, cursor = get_db()
    cursor.execute("SELECT username FROM users WHERE username=? AND password=?", (username, password))
    r = cursor.fetchone()
    conn.close()
    return bool(r)