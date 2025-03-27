# executor.py
import subprocess
import platform
import re
from database.db_handler import (
    add_blocked_entry, remove_blocked_entry, 
    list_blocked_entries, clear_blocked_entries
)
from logger.custom_logger import log_event, get_recent_logs

def check_network_impact(target, number):
    """Simulates the impact of blocking/unblocking an IP or port."""
    impact_report = f"Impact Analysis for {target} {number}:\n"

    try:
        if target == "ip":
            result = subprocess.run(["ping", "-n", "2", number], capture_output=True, text=True, timeout=5)
            if "Reply from" in result.stdout:
                impact_report += f"⚠️ Warning: IP {number} is active.\n"
            else:
                impact_report += f"✅ Safe: IP {number} is not responding.\n"

        elif target == "port":
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, timeout=5)
            if f":{number}" in result.stdout:
                impact_report += f"⚠️ Warning: Port {number} is in use.\n"
            else:
                impact_report += f"✅ Safe: Port {number} is not in use.\n"

    except Exception as e:
        impact_report += f"⚠️ Error checking {target}: {str(e)}\n"

    return impact_report

def execute_command(parsed_command):
    """
    Executes the parsed command and returns the result.
    """
    action = parsed_command["action"]
    target = parsed_command["target"]
    number = parsed_command["number"]

    # Log the action being performed
    log_event("system", f"Executing action: {action} on {target} {number}")

    if action == "unknown":
        return "Unknown command"

    if action == "show_blocked":
        # Show blocked entities (IPs/Ports)
        blocked_entries = list_blocked_entries()
        return f"Showing blocked IPs and Ports:\n{blocked_entries}"

    if action == "clear_blocked":
        # Clear all blocked entries
        cleared_message = clear_blocked_entries()
        log_event("system", "Cleared all blocked entries")
        return cleared_message

    if action == "show_logs":
        # Show the last 10 logs
        recent_logs = get_recent_logs()
        return f"Showing last 10 logs:\n{recent_logs}"

    if action == "invalid":
        return f"Invalid {target} number: {number}. Please provide a valid number."

    if target == "port":
        # Check if port number is valid
        if not number.isdigit() or int(number) < 1 or int(number) > 65535:
            return f"Invalid port number: {number}. Please provide a valid port number (1-65535)."

        # Simulate blocking a port
        add_blocked_entry("port", number)
        impact_report = check_network_impact("port", number)
        log_event("system", f"Blocked port: {number}")
        return f"(Simulation) Port {number} has been blocked.\n{impact_report}"

    if target == "ip":
        # Simulate blocking an IP address
        add_blocked_entry("ip", number)
        impact_report = check_network_impact("ip", number)
        log_event("system", f"Blocked IP: {number}")
        return f"(Simulation) IP {number} has been blocked.\n{impact_report}"

    return "Unknown command"
