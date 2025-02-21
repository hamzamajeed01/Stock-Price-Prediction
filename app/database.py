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
    
    # Create alerts table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS stock_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        stock_symbol TEXT,
                        frequency TEXT,
                        last_alert_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE(user_id, stock_symbol))"""
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


def save_stock_alert(user_id, stock_symbol, frequency):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO stock_alerts (user_id, stock_symbol, frequency, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, stock_symbol, frequency))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving stock alert: {e}")
        return False
    finally:
        conn.close()


def get_user_alerts(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT stock_symbol, frequency, last_alert_time
            FROM stock_alerts
            WHERE user_id = ?
        """, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting user alerts: {e}")
        return []
    finally:
        conn.close()


def delete_stock_alert(user_id, stock_symbol):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM stock_alerts
            WHERE user_id = ? AND stock_symbol = ?
        """, (user_id, stock_symbol))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting stock alert: {e}")
        return False
    finally:
        conn.close()


def get_alerts_by_frequency(frequency):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT sa.id, u.email, sa.stock_symbol, sa.frequency, sa.last_alert_time
            FROM stock_alerts sa
            JOIN users u ON sa.user_id = u.id
            WHERE sa.frequency = ?
        """, (frequency,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting alerts by frequency: {e}")
        return []
    finally:
        conn.close()


def update_last_alert_time(alert_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE stock_alerts
            SET last_alert_time = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (alert_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating last alert time: {e}")
        return False
    finally:
        conn.close()
