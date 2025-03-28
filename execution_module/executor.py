# executor.py

from config import CRITICAL_IPS, CRITICAL_PORTS
import subprocess
import platform
from database.db_handler import (
    add_blocked_entry, remove_blocked_entry,
    list_blocked_entries, clear_blocked_entries
)
from logger.custom_logger import log_event, get_recent_logs
from utils.safe_mode_handler import is_safe_mode, log_failsafe
from execution_module.iptables_utils import run_iptables_cmd, ensure_dummy_chain
from execution_module.rollback_handler import log_failsafe_entry

DUMMY_CHAIN = "NSMS_DUMMY"

def is_critical(target, number):
    """Checks if the target is marked as critical."""
    if target == "ip" and number in CRITICAL_IPS:
        return True
    if target == "port" and number in CRITICAL_PORTS:
        return True
    return False

def check_network_impact(target, number):
    """Performs impact analysis."""
    impact_report = f"Impact Analysis for {target} {number}:\n"
    try:
        if target == "ip":
            result = subprocess.run(
                ["ping", "-c", "2", number] if platform.system() != "Windows"
                else ["ping", "-n", "2", number],
                capture_output=True, text=True, timeout=5
            )
            if "bytes from" in result.stdout or "Reply from" in result.stdout:
                impact_report += f"⚠️ Warning: IP {number} is active.\n"
            else:
                impact_report += f"✅ Safe: IP {number} is not responding.\n"
        elif target == "port":
            result = subprocess.run(
                ["ss", "-lnt"] if platform.system() != "Windows" else ["netstat", "-an"],
                capture_output=True, text=True, timeout=5
            )
            if f":{number}" in result.stdout:
                impact_report += f"⚠️ Warning: Port {number} is in use.\n"
            else:
                impact_report += f"✅ Safe: Port {number} is not in use.\n"
    except Exception as e:
        impact_report += f"⚠️ Error checking {target}: {str(e)}\n"
    return impact_report

def execute_command(parsed_command):
    """Main command executor."""
    action = parsed_command["action"]
    target = parsed_command["target"]
    number = parsed_command["number"]

    if action == "unknown":
        return "Unknown command"

    if action in ["block", "unblock"] and is_safe_mode():
        return "❌ Safe Mode is ON. No changes allowed."

    if action in ["block", "unblock"] and is_critical(target, number):
        log_event("warning", f"Attempted to {action} critical {target}: {number} — operation denied.")
        return f"❌ ERROR: {target} {number} is marked as critical and cannot be {action}ed."

    log_event("system", f"Executing action: {action} on {target} {number}")

    ensure_dummy_chain()

    if action == "show_blocked":
        blocked_entries = list_blocked_entries()
        return f"Showing blocked IPs and Ports:\n{blocked_entries}"

    if action == "clear_blocked":
        run_iptables_cmd(["-F", DUMMY_CHAIN])
        cleared_message = clear_blocked_entries()
        log_event("system", "Cleared all blocked entries (dummy chain flushed)")
        return cleared_message

    if action == "show_logs":
        recent_logs = get_recent_logs()
        return f"Showing last 10 logs:\n{recent_logs}"

    if action == "invalid":
        return f"Invalid {target} number: {number}. Please provide a valid number."

    # Impact Analysis (only for blocking)
    if action == "block":
        impact = check_network_impact(target, number)
        if "Warning" in impact:
            log_event("warning", f"Impact detected on {target} {number} — action aborted.")
            return f"⚠️ Impact analysis warns that {target} {number} is currently active.\nAction aborted for safety.\n{impact}"
    else:
        impact = ""

    # Block / Unblock Logic
    if target == "port":
        if action == "block":
            add_blocked_entry("port", number)
            run_iptables_cmd(["-A", DUMMY_CHAIN, "-p", "tcp", "--dport", number, "-j", "DROP"])
            log_failsafe_entry(["-D", DUMMY_CHAIN, "-p", "tcp", "--dport", number, "-j", "DROP"])
            log_event("system", f"(Dummy) Blocked port {number}")
            return f"(Dummy) Port {number} has been blocked.\n{impact}"
        elif action == "unblock":
            remove_blocked_entry("port", number)
            run_iptables_cmd(["-D", DUMMY_CHAIN, "-p", "tcp", "--dport", number, "-j", "DROP"])
            log_event("system", f"(Dummy) Unblocked port {number}")
            log_failsafe("unblock", "port", number)
            return f"(Dummy) Port {number} has been unblocked."

    if target == "ip":
        if action == "block":
            add_blocked_entry("ip", number)
            run_iptables_cmd(["-A", DUMMY_CHAIN, "-s", number, "-j", "DROP"])
            log_failsafe_entry(["-D", DUMMY_CHAIN, "-s", number, "-j", "DROP"])
            log_event("system", f"(Dummy) Blocked IP {number}")
            return f"(Dummy) IP {number} has been blocked.\n{impact}"
        elif action == "unblock":
            remove_blocked_entry("ip", number)
            run_iptables_cmd(["-D", DUMMY_CHAIN, "-s", number, "-j", "DROP"])
            log_event("system", f"(Dummy) Unblocked IP {number}")
            log_failsafe("unblock", "ip", number)
            return f"(Dummy) IP {number} has been unblocked."

    return "Unknown command"
