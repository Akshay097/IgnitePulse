import json
import pytz
import os
from datetime import datetime

AUDIT_LOG_FILE = "audit_log.json"

def load_audit_log():
    if os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []  # fallback if wrong type
            except:
                return []
    return []

def save_audit_log(logs):
    with open(AUDIT_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_audit_entry(email, timestamp, device_id, ip, status, reason=""):
    logs = load_audit_log()
    entry = {
        "email": email,
        "timestamp": timestamp,
        "device_id": device_id,
        "ip": ip,
        "status": status,
        "reason": reason
    }
    logs.append(entry)
    save_audit_log(logs)
    print(f"📋 Audit log → {status} for {email}: {reason}", flush=True)

def detect_device_sharing(device_id, email):
    logs = load_audit_log()
    users_on_device = set(
        log["email"] for log in logs
        if log["device_id"] == device_id and log["email"] != email
    )
    return bool(users_on_device)

def detect_multiple_ips(email, ip):
    logs = load_audit_log()
    known_ips = set(
        log["ip"] for log in logs
        if log["email"] == email and log["ip"] != ip
    )
    return bool(known_ips)
