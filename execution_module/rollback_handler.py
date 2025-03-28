# execution_module/rollback_handler.py

from logger.custom_logger import log_event
from execution_module.iptables_utils import run_iptables_cmd

ROLLBACK_LOG_FILE = "rollback_log.txt"

def log_failsafe_entry(rule):
    """Logs iptables rule for rollback."""
    try:
        with open(ROLLBACK_LOG_FILE, "a") as f:
            f.write(" ".join(rule) + "\n")
        log_event("system", f"Logged rollback rule: {' '.join(rule)}")
    except Exception as e:
        log_event("error", f"Failed to log rollback rule: {str(e)}")

def perform_rollback():
    """Applies rollback by removing logged iptables rules (in reverse order)."""
    try:
        with open(ROLLBACK_LOG_FILE, "r") as f:
            rules = f.readlines()

        for rule in reversed(rules):
            rule = rule.strip().split()
            if rule:
                success, msg = run_iptables_cmd(rule)
                if success:
                    log_event("system", f"Rolled back: {' '.join(rule)}")
                else:
                    log_event("error", f"Failed to rollback: {' '.join(rule)}")

        # Clear rollback log safely
        with open(ROLLBACK_LOG_FILE, "w") as f:
            pass

        log_event("system", "Rollback completed and log cleared.")
        return "Rollback completed."

    except FileNotFoundError:
        return "Rollback log not found."

    except Exception as e:
        return f"Error during rollback: {str(e)}"
