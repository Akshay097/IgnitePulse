import json
import os
from datetime import datetime

AUDIT_LOG_FILE = "audit_log.json"

def load_audit_log():
    if os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_audit_log(logs):
    with open(AUDIT_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_audit_entry(entry_type, email, detail, device_id=None, ip=None):
    logs = load_audit_log()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "type": entry_type,
        "email": email,
        "detail": detail,
        "timestamp": now,
        "device_id": device_id,
        "ip": ip
    }
    logs.append(entry)
    save_audit_log(logs)
    print(f"📋 Audit log → {entry_type} for {email}: {detail}", flush=True)

def detect_device_sharing(device_id, email):
    logs = load_audit_log()
    users_on_device = set(
        log["email"] for log in logs
        if log["device_id"] == device_id and log["email"] != email
    )
    if users_on_device:
        detail = f"Device used by multiple users: {', '.join(users_on_device)}"
        log_audit_entry("device_sharing", email, detail, device_id=device_id)
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
        log_audit_entry("multi_ip", email, detail, ip=ip)
        return True
    return False
