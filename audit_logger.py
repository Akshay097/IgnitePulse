import json
import os
from datetime import datetime

AUDIT_LOG_FILE = "audit_log.json"

def load_audit_log():
    """Load audit log (always as list)."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    try:
        with open(AUDIT_LOG_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except Exception:
        return []

def save_audit_log(logs):
    """Save audit log (as list)."""
    with open(AUDIT_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_audit_entry(email, timestamp, device_id, ip, status, reason=""):
    """Append new audit entry."""
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
    """Detect if device_id used for multiple emails."""
    logs = load_audit_log()
    users_on_device = set(
        log["email"] for log in logs
        if log["device_id"] == device_id and log["email"] != email
    )
    if users_on_device:
        print(f"🚩 Device Sharing detected: {device_id} used by {', '.join(users_on_device)}")
        return True
    return False

def detect_multiple_ips(email, ip):
    """Detect if email has used multiple IPs."""
    logs = load_audit_log()
    known_ips = set(
        log["ip"] for log in logs
        if log["email"] == email and log["ip"] != ip
    )
    if known_ips:
        print(f"🚩 Multiple IPs detected for {email}: {', '.join(known_ips)}")
        return True
    return False
