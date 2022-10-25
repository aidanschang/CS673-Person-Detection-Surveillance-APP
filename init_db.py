"""Script to initialize database with table and example row."""
import sqlite3

connection = sqlite3.connect("database.db")


with open("db/schema.sql") as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute(
    "INSERT INTO files (filename, user) VALUES (?, ?)",
    ("dog.jpg", "test@email.com"),
)

cur.execute("DROP TABLE IF EXISTS users;")

cur.execute(
    "CREATE TABLE users (email VARCHAR(255), name VARCHAR(255), password"
    " VARCHAR(255), alert VARCHAR(255), alert_interval INTEGER NOT NULL"
    " DEFAULT 1, last_alert TIMESTAMP DEFAULT (DATETIME('now', 'localtime')))"
)

cur.execute(
    "INSERT INTO users (email, name,password) VALUES (?, ?, ?)",
    ("admin@admin.com", "admin", "admin"),
)


connection.commit()
connection.close()
