from nlp_module.parser import parse_command
from execution_module.executor import execute_command

def main():
    print("Network Security Management System - Text Command Interface")
    print("Type a command (e.g., 'Block port 22', 'Block IP 192.168.1.100', 'Show blocked', 'Unblock IP 192.168.1.100') or type 'exit' to quit.")

    while True:
        user_input = input("\nEnter command: ")
        if user_input.lower() == "exit":
            print("Exiting system...")
            break
        
        parsed_cmd = parse_command(user_input)
        print(f"Parsed Command: {parsed_cmd}")
        
        result = execute_command(parsed_cmd)
        print(f"Execution Result: {result}")

if __name__ == "__main__":
    main()
