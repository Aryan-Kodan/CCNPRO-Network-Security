import sqlite3
import secrets
from flask_bcrypt import Bcrypt

DB_PATH = "D:/CCNPRO/database/security.db"
bcrypt = Bcrypt()

def init_db():
    """Creates necessary tables for blocked entries, users, and API tokens."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Table for blocked entries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                number TEXT NOT NULL UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for user authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
            )
        ''')
        
        # Table for API tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()

def add_blocked_entry(target, number):
    """Adds an entry to the blocked list in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO blocked_entries (target, number) VALUES (?, ?)", (target, number))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Avoid duplicate entries

def remove_blocked_entry(target, number):
    """Removes an entry from the blocked list."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blocked_entries WHERE target=? AND number=?", (target, number))
        conn.commit()

def list_blocked_entries():
    """Returns all blocked IPs and ports."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target, number FROM blocked_entries")
        entries = cursor.fetchall()
    return "\n".join(f"{target} {number}" for target, number in entries) if entries else "No blocked entries found."

def clear_blocked_entries():
    """Clears all blocked IPs and ports."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blocked_entries")
        conn.commit()
    return "All blocked entries have been cleared."

# ✅ Ensure database is initialized on import
init_db()

def create_user(username, password, role="user"):
    """Registers a new user with a hashed password."""
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                           (username, password_hash, role))
            conn.commit()
            return f"User '{username}' created successfully as {role}."
        except sqlite3.IntegrityError:
            return f"Error: Username '{username}' already exists."

def validate_user(username, password):
    """Validates user credentials and returns role if correct."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user[0], password):
            return user[1]  # Return role
    return None  # Invalid credentials

def generate_api_token(user_id):
    """Generates a unique API token for a user."""
    token = secrets.token_hex(32)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO api_tokens (user_id, token) VALUES (?, ?)", (user_id, token))
        conn.commit()
    return token

def validate_api_token(token):
    """Validates API token and returns user role if valid."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT users.role FROM api_tokens JOIN users ON api_tokens.user_id = users.id WHERE api_tokens.token = ?", (token,))
        user = cursor.fetchone()
        return user[0] if user else None  # Return role if token is valid

# ✅ Initialize database on import
init_db()
