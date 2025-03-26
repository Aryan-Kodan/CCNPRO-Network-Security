from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
from config import ALLOWED_IPS
from nlp_module.parser import parse_command
from execution_module.executor import execute_command
from database.db_handler import init_db, create_user, validate_user, validate_api_token, generate_api_token
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Initialize database
init_db()

def get_client_ip():
    """Extracts the real client IP."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0]
    return request.remote_addr

@app.before_request
def restrict_access():
    """Blocks requests from non-allowed IPs unless authenticated."""
    client_ip = get_client_ip()
    if client_ip not in ALLOWED_IPS and "username" not in session:
        abort(403)

@app.route("/")
def index():
    """Home page with login/logout options."""
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
            return redirect(url_for("index"))
        return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logs out a user."""
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))

@app.route("/api/token", methods=["POST"])
def get_api_token():
    """Generates an API token for authenticated users."""
    if "username" not in session:
        abort(403)

    username = session["username"]
    with sqlite3.connect("D:/CCNPRO/database/security.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404  # ✅ Fixed missing user error

    token = generate_api_token(user[0])
    return jsonify({"api_token": token})

@app.route("/execute", methods=["POST"])
def execute():
    """Handles command execution with session authentication."""
    
    # ✅ Ensure user is logged in via session
    if "username" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 403
    
    # ✅ Get user role from session
    role = session["role"]
    
    # ✅ Get command from request
    data = request.get_json()
    user_command = data.get("command", "").strip()

    # ✅ Prevent empty command execution
    if not user_command:
        return jsonify({"error": "No command provided"}), 400

    # ✅ Restrict non-admin users from blocking/unblocking
    if role != "admin" and ("block" in user_command or "unblock" in user_command):
        return jsonify({"error": "Permission denied"}), 403

    # ✅ Parse & execute the command
    parsed_command = parse_command(user_command)
    result = execute_command(parsed_command)

    return jsonify({
        "parsed_command": parsed_command,
        "execution_result": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
