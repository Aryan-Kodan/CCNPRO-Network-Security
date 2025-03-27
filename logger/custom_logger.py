import logging
import os
from datetime import datetime

LOG_FILE = "D:/CCNPRO/logs/security.log"

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_event(event_type, message):
    """Logs events with different severity levels."""
    log_message = f"{event_type.upper()}: {message}"
    if event_type == "error":
        logging.error(log_message)
    elif event_type == "warning":
        logging.warning(log_message)
    else:
        logging.info(log_message)

def get_recent_logs(limit=10):
    """Retrieves the last 'limit' log entries."""
    try:
        with open(LOG_FILE, "r") as file:
            logs = file.readlines()[-limit:]
        return "".join(logs) if logs else "No logs found."
    except FileNotFoundError:
        return "Log file not found."
