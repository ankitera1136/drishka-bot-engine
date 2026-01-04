import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

books = [
    ("Clean Code", "Robert C. Martin"),
    ("Atomic Habits", "James Clear"),
    ("Deep Learning", "Ian Goodfellow"),
    ("Python Crash Course", "Eric Matthes")
]

cursor.executemany(
    "INSERT INTO books (title, author) VALUES (?, ?)",
    books
)

conn.commit()
conn.close()
print("📚 Sample books added")
