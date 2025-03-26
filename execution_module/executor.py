import subprocess
import platform
from database.db_handler import add_blocked_entry, remove_blocked_entry, list_blocked_entries, clear_blocked_entries

def check_network_impact(target, number):
    """Simulates the impact of blocking/unblocking an IP or port."""
    impact_report = f"Impact Analysis for {target} {number}:\n"

    if target == "ip":
        try:
            result = subprocess.run(["ping", "-n", "2", number], capture_output=True, text=True, timeout=5)
            if "Reply from" in result.stdout:
                impact_report += f"⚠️ Warning: IP {number} is currently active.\n"
            else:
                impact_report += f"✅ Safe: IP {number} is not responding.\n"
        except Exception as e:
            impact_report += f"⚠️ Error checking IP: {str(e)}\n"

    if target == "port":
        try:
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, timeout=5)
            if f":{number}" in result.stdout:
                impact_report += f"⚠️ Warning: Port {number} is in use.\n"
            else:
                impact_report += f"✅ Safe: Port {number} is not in use.\n"
        except Exception as e:
            impact_report += f"⚠️ Error checking port: {str(e)}\n"

    return impact_report

def execute_command(parsed_command):
    """Executes security commands using the SQLite database."""
    action = parsed_command["action"]
    target = parsed_command["target"]
    number = parsed_command["number"]

    if action == "show_blocked":
        return list_blocked_entries()

    if action == "clear_blocked":
        return clear_blocked_entries()

    if action in ["block", "unblock"] and target in ["port", "ip"] and number:
        impact_report = check_network_impact(target, number)

        if action == "block":
            add_blocked_entry(target, number)
            result = f"(Simulation) {target} {number} has been blocked.\n" + impact_report

        elif action == "unblock":
            remove_blocked_entry(target, number)
            result = f"(Simulation) {target} {number} has been unblocked.\n" + impact_report

        return result

    return "Unknown command"
