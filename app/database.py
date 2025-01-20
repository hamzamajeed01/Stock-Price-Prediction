import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash


def create_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT UNIQUE,
                        password TEXT)"""
    )

    conn.commit()
    conn.close()


def add_user(first_name, last_name, email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if user:
        conn.close()
        return False  

    hashed_password = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
        (first_name, last_name, email, hashed_password),
    )

    conn.commit()
    conn.close()
    return True


def authenticate_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user[4], password):
        return True
    return False
