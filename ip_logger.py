import json
import os
from datetime import datetime

IP_LOG_FILE = "ip_log.json"

def load_ip_logs():
    if os.path.exists(IP_LOG_FILE):
        with open(IP_LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_ip_logs(logs):
    with open(IP_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_client_ip(request):
    """
    Extract real client IP, even behind proxy (Render uses proxy).
    """
    if request.headers.get('X-Forwarded-For'):
        # In Render, X-Forwarded-For might contain multiple IPs, take first
        forwarded_for = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return forwarded_for
    return request.remote_addr

def log_user_ip(email, ip):
    """
    Log user's IP history locally (this is not pushed to Google Sheet).
    """
    logs = load_ip_logs()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if email not in logs:
        logs[email] = []
    logs[email].append({"ip": ip, "timestamp": now})
    save_ip_logs(logs)
    print(f"🛡️ Logged IP for {email}: {ip} at {now}", flush=True)

def is_ip_suspicious(email, ip):
    """
    Check if this email has logged in from multiple IP addresses.
    """
    logs = load_ip_logs()
    entries = logs.get(email, [])
    known_ips = {entry["ip"] for entry in entries}
    if len(known_ips) > 1 and ip not in known_ips:
        print(f"🚨 Suspicious IP detected for {email}: {ip}", flush=True)
        return True
    return False
