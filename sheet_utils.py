import os
import datetime
import gspread
import pytz
import json
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 🔐 Credential setup
if os.path.exists("credentials.json"):
    CREDENTIALS_PATH = "credentials.json"
    print("🔐 Using local credentials.json", flush=True)
else:
    CREDENTIALS_PATH = "/etc/secrets/credentials.json"
    print("🔐 Using deployed secret credentials.json", flush=True)

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
    client = gspread.authorize(creds)
    print("✅ Google Sheets authorized successfully", flush=True)
except Exception as e:
    client = None
    print("❌ Failed to authorize Google Sheets:", str(e), flush=True)


def log_attendance(email, lat, lon, timestamp, status, device_id=None, ip=None, note=""):
    if not client:
        print("⚠️ Skipping Google Sheet write: client not available", flush=True)
        return

    try:
        atlantic = pytz.timezone("Canada/Atlantic")
        sheet_title = datetime.datetime.now(atlantic).strftime("%m-%d-%Y")
        spreadsheet = client.open("IgnitePulse")

        try:
            worksheet = spreadsheet.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            print(f"📄 Creating new sheet tab: {sheet_title}", flush=True)
            worksheet = spreadsheet.add_worksheet(title=sheet_title, rows="100", cols="12")
            worksheet.append_row([
                "Email", "Latitude", "Longitude", "Status", "Timestamp",
                "Device ID", "IP Address", "Reason"
            ])

        worksheet.append_row([
            email, lat, lon, status, timestamp,
            device_id or "N/A", ip or "N/A", note or ""
        ])
        print("✅ Row logged successfully", flush=True)

    except Exception as e:
        import traceback
        print("⚠️ Error logging attendance:", flush=True)
        traceback.print_exc()


def log_audit(email, timestamp, ip, device_id, lat, lon):
    try:
        AUDIT_FILE = "audit_log.json"

        if not os.path.exists(AUDIT_FILE):
            with open(AUDIT_FILE, "w") as f:
                json.dump({}, f)

        with open(AUDIT_FILE, "r") as f:
            audit_data = json.load(f)

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        if email not in audit_data:
            audit_data[email] = {}

        if today not in audit_data[email]:
            audit_data[email][today] = []

        for entry in audit_data[email][today]:
            if entry["device_id"] == device_id:
                print(f"🚫 Device {device_id} already submitted today for {email}")
                return True  # already submitted

        audit_data[email][today].append({
            "time": timestamp,
            "ip": ip,
            "device_id": device_id,
            "lat": lat,
            "lon": lon
        })

        with open(AUDIT_FILE, "w") as f:
            json.dump(audit_data, f, indent=2)

        print(f"📝 Audit logged for {email} at {timestamp}")
        return False

    except Exception as e:
        print("⚠️ Error in audit logging:", str(e))
        return False


def check_device_binding(email, device_id):
    BIND_FILE = "binding.json"
    if not os.path.exists(BIND_FILE):
        return False

    with open(BIND_FILE, "r") as f:
        bindings = json.load(f)

    return bindings.get(email) == device_id


def bind_device(email, device_id):
    BIND_FILE = "binding.json"
    if not os.path.exists(BIND_FILE):
        with open(BIND_FILE, "w") as f:
            json.dump({}, f)

    with open(BIND_FILE, "r") as f:
        bindings = json.load(f)

    bindings[email] = device_id

    with open(BIND_FILE, "w") as f:
        json.dump(bindings, f, indent=2)

    print(f"🔒 Device bound: {email} → {device_id}")
