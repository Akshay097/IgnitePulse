import os
import json
from datetime import datetime

# Files for storing device bindings and submission history
BINDING_FILE = "binding.json"
SUBMISSION_LOG = "submission_log.json"

# Ensure files exist
for file in [BINDING_FILE, SUBMISSION_LOG]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)

def get_device_id_from_request(request):
    """Extract device_id sent from client"""
    try:
        data = request.json
        return data.get("device_id")
    except:
        return None

# Device Binding Logic 🔒

def check_device_binding(email, device_id):
    """Check if device is allowed (bound) for user"""
    with open(BINDING_FILE, "r") as f:
        bindings = json.load(f)
    return bindings.get(email) == device_id

def bind_device(email, device_id):
    """Bind first device to user"""
    with open(BINDING_FILE, "r") as f:
        bindings = json.load(f)

    if email not in bindings:
        bindings[email] = device_id
        with open(BINDING_FILE, "w") as f:
            json.dump(bindings, f, indent=2)
        print(f"✅ New device bound → {email}: {device_id}")
    else:
        print(f"ℹ️ Device already bound for {email}")

# Daily Submission Control (if needed) ✅

def has_already_submitted(email, date_str):
    """Prevent multiple submissions per day (optional feature)"""
    with open(SUBMISSION_LOG, "r") as f:
        submissions = json.load(f)
    return email in submissions and submissions[email] == date_str

def log_submission(email):
    """Log today's submission"""
    today = datetime.now().strftime("%Y-%m-%d")
    with open(SUBMISSION_LOG, "r") as f:
        submissions = json.load(f)
    submissions[email] = today
    with open(SUBMISSION_LOG, "w") as f:
        json.dump(submissions, f, indent=2)
