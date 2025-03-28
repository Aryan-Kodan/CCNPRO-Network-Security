# utils/safe_mode_handler.py

SAFE_MODE_FILE = "safe_mode.flag"

def is_safe_mode():
    """Check if safe mode is enabled."""
    try:
        with open(SAFE_MODE_FILE, "r") as f:
            return f.read().strip() == "ON"
    except FileNotFoundError:
        return False

def set_safe_mode(state):
    """Enable or disable safe mode."""
    with open(SAFE_MODE_FILE, "w") as f:
        f.write("ON" if state else "OFF")

def log_failsafe(action, target, number):
    """Log simple failsafe events (placeholder for extension)."""
    # You can expand this later if you want
    pass
