import sqlite3

DB_NAME = "library.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    joined_on TEXT
)
""")

# BOOKS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    available INTEGER DEFAULT 1
)
""")

# BORROWED BOOKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS borrow (
    borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    due_date TEXT,
    returned INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(book_id) REFERENCES books(book_id)
)
""")

# FEES / PAYMENTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS fees (
    user_id INTEGER,
    amount INTEGER,
    reason TEXT,
    paid INTEGER DEFAULT 0
)
""")

# ANNOUNCEMENTS (for broadcast history)
cursor.execute("""
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    sent_on TEXT
)
""")

# STUDENTS (Reading Room Members)
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    user_id INTEGER PRIMARY KEY,
    seat_no TEXT,
    fee INTEGER,
    due_date TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully")
