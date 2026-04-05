import sqlite3

def get_connection():
    return sqlite3.connect('food_hero.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Ensure all tables exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS food (id INTEGER PRIMARY KEY AUTOINCREMENT, restaurant TEXT, type TEXT, quantity INTEGER, status TEXT, location TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, food_id INTEGER, home TEXT, requested_qty INTEGER, allocated_qty INTEGER, status TEXT)''')
    conn.commit()
    conn.close()