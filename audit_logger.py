import json
import os
from datetime import datetime
import pytz

AUDIT_LOG_FILE = "audit_log.json"

def load_audit_log():
    if os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, "r") as f:
            return json.load(f)
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
    print(f"📝 Audit logged for {email} at {timestamp}", flush=True)

def detect_device_sharing(device_id, email):
    logs = load_audit_log()
    users_on_device = set(
        log["email"] for log in logs
        if log["device_id"] == device_id and log["email"] != email
    )
    if users_on_device:
        detail = f"Device used by multiple users: {', '.join(users_on_device)}"
        print(f"⚠️ {detail}", flush=True)
        return True
    return False

def detect_multiple_ips(email, ip):
    logs = load_audit_log()
    known_ips = set(
        log["ip"] for log in logs
        if log["email"] == email and log["ip"] != ip and log["ip"] is not None
    )
    if known_ips:
        detail = f"Multiple IPs detected: {', '.join(known_ips)}"
        print(f"⚠️ {detail}", flush=True)
        return True
    return False
