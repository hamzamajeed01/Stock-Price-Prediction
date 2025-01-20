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
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
            return None  # User already exists

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, hashed_password),
        )
        conn.commit()
        
        # Fetch the newly created user to return their data
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        new_user = cursor.fetchone()
        return new_user
        
    except Exception as e:
        print(f"Error adding user: {e}")
        return None
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[4], password):
            return user  # Return the entire user tuple
        return None
        
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()