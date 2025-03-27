#db_handle.py
import sqlite3
import secrets
from flask_bcrypt import Bcrypt

DB_PATH = "D:/CCNPRO/database/security.db"
bcrypt = Bcrypt()

def init_db():
    """Creates necessary tables for blocked entries, users, API tokens, and logs."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Table for blocked entries (IPs and Ports)
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

        # Table for logging executed commands
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                command TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()

def log_command(username, command):
    """Stores executed commands in the logs table."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (username, command) VALUES (?, ?)", (username, command))
        conn.commit()

def get_last_logs(limit=10):
    """Retrieves the last N executed commands from logs."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, command, timestamp FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        logs = cursor.fetchall()
    
    return "\n".join(f"{log[2]} - {log[0]}: {log[1]}" for log in logs) if logs else "No logs found."

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
    """Unblocks all IPs/ports before clearing the blocked list."""
    from execution_module.executor import execute_command  # Import here to avoid circular import issues

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Get all blocked entries before deleting
        cursor.execute("SELECT target, number FROM blocked_entries")
        entries = cursor.fetchall()

        # Unblock each entry before deleting
        for target, number in entries:
            execute_command({"action": "unblock", "target": target, "number": number})

        # Now clear the database
        cursor.execute("DELETE FROM blocked_entries")
        conn.commit()

    return f"✅ All {len(entries)} blocked entries have been unblocked and removed."

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

def get_blocked_entities():
    """Fetch blocked IPs and Ports from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target, number FROM blocked_entries")
        blocked_entries = cursor.fetchall()

    # Format results as lists
    blocked_ips = [entry[1] for entry in blocked_entries if entry[0] == "ip"]
    blocked_ports = [entry[1] for entry in blocked_entries if entry[0] == "port"]

    return blocked_ips, blocked_ports

# ✅ Initialize database on import
init_db()
