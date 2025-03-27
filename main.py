# main.py
from nlp_module.parser import parse_command
from execution_module.executor import execute_command
from logger.custom_logger import log_event

def main():
    print("Network Security Management System - Text Command Interface")
    print("Type a command (e.g., 'Block port 22', 'Block IP 192.168.1.100', 'Show blocked', 'Unblock IP 192.168.1.100') or type 'exit' to quit.")

    while True:
        user_input = input("\nEnter command: ")

        # Exit condition
        if user_input.lower() == "exit":
            print("Exiting system...")
            log_event("system", "Exited the system.")
            break
        
        # Parse the command using the NLP module
        parsed_cmd = parse_command(user_input)
        print(f"Parsed Command: {parsed_cmd}")

        # Execute the parsed command and get the result
        result = execute_command(parsed_cmd)
        print(f"Execution Result: {result}")

        # Log the executed command
        log_event("system", f"Executed command: {user_input}")

if __name__ == "__main__":
    main()
