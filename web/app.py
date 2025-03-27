# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
from config import ALLOWED_IPS
from nlp_module.parser import parse_command
from execution_module.executor import execute_command
from database.db_handler import init_db, validate_user
from logger.custom_logger import log_event, get_recent_logs

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Initialize database
init_db()

def get_client_ip():
    """Extracts client IP address."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0]
    return request.remote_addr

@app.before_request
def restrict_access():
    """Restricts access to allowed IPs."""
    client_ip = get_client_ip()
    if client_ip not in ALLOWED_IPS and "username" not in session:
        log_event("warning", f"Unauthorized access attempt from {client_ip}")
        abort(403)

@app.route("/")
def index():
    """Homepage with login/logout options."""
    if "username" in session:
        return render_template("dashboard.html", username=session["username"], role=session["role"])
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = validate_user(username, password)

        if role:
            session["username"] = username
            session["role"] = role
            log_event("info", f"User '{username}' logged in.")
            return redirect(url_for("index"))

        log_event("warning", f"Failed login attempt for username '{username}'")
        return "Invalid credentials", 401

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logs out a user."""
    log_event("info", f"User '{session.get('username', 'Unknown')}' logged out.")
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))

@app.route("/execute", methods=["POST"])
def execute():
    """Handles command execution."""
    if "username" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 403

    role = session["role"]
    data = request.get_json()
    user_command = data.get("command", "").strip()

    if not user_command:
        return jsonify({"error": "No command provided"}), 400

    # Permission check for "block" and "unblock" actions
    if role != "admin" and ("block" in user_command or "unblock" in user_command):
        log_event("warning", f"Unauthorized command attempt: {user_command}")
        return jsonify({"error": "Permission denied"}), 403

    parsed_command = parse_command(user_command)
    result = execute_command(parsed_command)

    return jsonify({
        "parsed_command": parsed_command,
        "execution_result": result
    })

@app.route("/logs")
def logs():
    """Displays the last 10 logs."""
    return jsonify({"recent_logs": get_recent_logs()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
