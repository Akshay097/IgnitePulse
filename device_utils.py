import os
import json
from datetime import datetime

BINDING_FILE = "binding.json"
SUBMISSION_LOG = "submission_log.json"

# Initialize files if they don't exist
if not os.path.exists(BINDING_FILE):
    with open(BINDING_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(SUBMISSION_LOG):
    with open(SUBMISSION_LOG, "w") as f:
        json.dump({}, f)


def get_device_id_from_request(request):
    """Extract device_id from incoming JSON request body."""
    try:
        data = request.json
        return data.get("device_id")
    except:
        return None


def is_device_allowed(email, device_id):
    with open(BINDING_FILE, "r") as f:
        bindings = json.load(f)

    if email not in bindings:
        return True  # First-time device use
    return bindings[email] == device_id


def bind_device_to_user(email, device_id):
    with open(BINDING_FILE, "r") as f:
        bindings = json.load(f)

    bindings[email] = device_id

    with open(BINDING_FILE, "w") as f:
        json.dump(bindings, f, indent=2)


def has_already_submitted(email, date_str):
    with open(SUBMISSION_LOG, "r") as f:
        submissions = json.load(f)

    return email in submissions and submissions[email] == date_str


def log_submission(email):
    today = datetime.now().strftime("%Y-%m-%d")

    with open(SUBMISSION_LOG, "r") as f:
        submissions = json.load(f)

    submissions[email] = today

    with open(SUBMISSION_LOG, "w") as f:
        json.dump(submissions, f, indent=2)
