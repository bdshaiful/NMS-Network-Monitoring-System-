from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
import platform
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = "super-secret-key-please-change"

# Define users (lowercase keys for case-insensitive login)
users = {
    "admin": "Admin",
    "admin2": "Admin2"
}

# Devices
devices = [
    {"ip": "(your IP)", "name": "Description", "group": "Core"},
    {"ip": "10.25.55.3", "name": "Description", "group": "14th Floor"},
    {"ip": "10.25.55.10", "name": "14th flr Down Switch East", "group": "14th Floor"},
    {"ip": "10.25.55.4", "name": "14th flr Up Switch West", "group": "14th Floor"},
    {"ip": "10.25.55.9", "name": "14th flr Down Switch West", "group": "14th Floor"},    
    {"ip": "10.25.55.11", "name": "13Flr Canteen UP Switch", "group": "13th Floor"},
    {"ip": "10.25.55.20", "name": "13Flr Canteen Down Switch", "group": "13th Floor"},
    {"ip": "10.25.55.21", "name": "13Flr East UP Switch", "group": "13th Floor"},
    {"ip": "10.25.55.23", "name": "13Flr East Down Switch", "group": "13th Floor"},
    {"ip": "10.25.55.101", "name": "14flr CEO AP", "group": "APs"},
    {"ip": "10.25.55.102", "name": "14Flr Frnt IT Room AP", "group": "APs"},
    {"ip": "10.25.55.103", "name": "14Flr Meeting Room AP", "group": "APs"},
    {"ip": "10.25.55.104", "name": "14Flr Breakoutzone AP", "group": "APs"},
    {"ip": "10.25.55.105", "name": "13flr Display Area AP", "group": "APs"},
    {"ip": "10.25.55.106", "name": "13flr Meeting room AP", "group": "APs"},
    {"ip": "10.25.55.107", "name": "13flr HR Area AP", "group": "APs"},
    {"ip": "182.25.1.40", "name": "Test IP", "group": "Others"},
    {"ip": "10.25.88.2", "name": "NVR", "group": "External"},
    {"ip": "10.1.130.212", "name": "Mail Server", "group": "External"},
    {"ip": "8.8.8.8", "name": "Google DNS", "group": "External"},
    {"ip": "4.4.4.4", "name": "Google Alt DNS", "group": "External"},
]

# Platform-aware ping command
def get_ping_command(ip):
    count_flag = "-n" if platform.system().lower() == "windows" else "-c"
    return ["ping", count_flag, "1", ip]

# Ping device function
def ping_device(device):
    start = time.time()
    try:
        result = subprocess.run(
            get_ping_command(device["ip"]),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2
        )
        latency = round((time.time() - start) * 1000)
        success = result.returncode == 0
        return {**device, "status": success, "latency": latency if success else None}
    except Exception:
        return {**device, "status": False, "latency": None}

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if username in users and users[username] == password:
            session["logged_in"] = True
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

# Protected dashboard
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

# Protected status endpoint
@app.route("/status")
def status():
    if not session.get("logged_in"):
        return jsonify({"error": "unauthorized"}), 401
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(ping_device, devices))
    return jsonify(results)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
