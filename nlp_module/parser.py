# parser.py
import re
def parse_command(user_input):
    """
    Parses user input and extracts action, target, and number.
    
    Recognized Commands:
    - Block IP 192.168.1.100
    - Block port 22
    - Unblock IP 192.168.1.100
    - Unblock port 22
    - Show blocked
    - Clear blocked
    - Show logs
    """

    # Convert input to lowercase and remove extra spaces
    user_input = user_input.lower().strip()

    # Default structure for parsed command
    parsed_command = {"action": "unknown", "target": "unknown", "number": None}

    # ✅ Show all blocked IPs and ports
    if user_input == "show blocked":
        parsed_command["action"] = "show_blocked"
        parsed_command["target"] = "blocked"
        return parsed_command

    # ✅ Clear all blocked IPs and ports
    if user_input == "clear blocked":
        parsed_command["action"] = "clear_blocked"
        parsed_command["target"] = "blocked"
        return parsed_command

    # ✅ Show security logs
    if user_input == "show logs":
        parsed_command["action"] = "show_logs"
        return parsed_command

    # ✅ Handle Block and Unblock commands
    words = user_input.split()
    if len(words) == 3:
        action, target, number = words

        if action in ["block", "unblock"]:
            parsed_command["action"] = action

            if target == "ip":
                parsed_command["target"] = "ip"
                # Validate the IP format
                if re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", number):
                    parsed_command["number"] = number  # Example: 192.168.1.100
                else:
                    parsed_command["action"] = "invalid"
                    parsed_command["target"] = "ip"
                    parsed_command["number"] = number  # Invalid IP format

            elif target == "port":
                # Ensure that port is a valid number within range
                if number.isdigit() and 1 <= int(number) <= 65535:
                    parsed_command["target"] = "port"
                    parsed_command["number"] = number  # Example: 22
                else:
                    parsed_command["action"] = "invalid"
                    parsed_command["target"] = "port"
                    parsed_command["number"] = number  # Invalid port number

            return parsed_command

    return parsed_command  # If no match, return default unknown structure
