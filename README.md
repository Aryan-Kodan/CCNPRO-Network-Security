# Network Security Management System

## **Overview**
The **Network Security Management System** is a command-line tool designed to manage security rules dynamically. It allows users to **block and unblock IPs and ports**, list blocked entries, and retrieve logs of security actions.

## **Features**
- **Block IPs and Ports** – Restrict access by blocking specific IP addresses or ports.
- **Unblock IPs and Ports** – Remove security rules safely after verification.
- **Check Before Unblocking** – Ensures an IP/Port is actually blocked before unblocking.
- **List Blocked Entries** – View all currently blocked IPs and ports.
- **View Logs** – Retrieve the last 10 security actions.
- **Prevents Duplicate Entries** – Avoids redundant blocking of IPs/ports.

## **Folder Structure**
# Project root 
│── venv\ # Virtual environment 
│── logs\ # Stores logs 
│ ├── security_log.txt # Log file for executed commands 
│ ├── blocked_list.txt # Stores blocked IPs/ports 
│── nlp_module\ # NLP processing folder 
│ ├── init.py # Package initialization 
│ ├── parser.py # Parses user commands 
│── execution_module\ # Command execution logic 
│ ├── init.py # Package initialization 
│ ├── executor.py # Handles blocking/unblocking logic 
│── main.py # Entry point for testing 
│── requirements.txt # Dependencies file 
│── README..txt # Project documentation