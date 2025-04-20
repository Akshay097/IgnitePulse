import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
if os.path.exists("/etc/secrets/credentials.json"):
    print("🔐 Loading credentials from: /etc/secrets/credentials.json", flush=True)
    CREDENTIALS_PATH = "/etc/secrets/credentials.json"
else:
    print("🔐 Loading credentials from: credentials.json (local)", flush=True)
    CREDENTIALS_PATH = "credentials.json"

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
    client = gspread.authorize(creds)
    print("✅ Google Sheets authorized successfully", flush=True)
except Exception as e:
    print("❌ Failed to authorize Google Sheets:", str(e), flush=True)
    client = None

def log_attendance(email, lat, lon, timestamp, status):
    if not client:
        print("⚠️ Skipping Google Sheet write: client not available", flush=True)
        return

    try:
        sheet = client.open("Ignitemeetup Attendance").worksheet("Sheet1")

        sheet_title = datetime.datetime.now().strftime("%m-%d-%Y")
        try:
            worksheet = client.open("Ignitemeetup Attendance").worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            print(f"📄 Creating new sheet tab: {sheet_title}", flush=True)
            worksheet = client.open("Ignitemeetup Attendance").add_worksheet(title=sheet_title, rows="100", cols="10")
            worksheet.append_row(["Email", "Latitude", "Longitude", "Status", "Timestamp"])

        print(f"📥 Logging attendance for: {email}", flush=True)
        print(f"📍 Location: {lat}, {lon} | Status: {status} | Time: {timestamp}", flush=True)
        print(f"📄 Using sheet tab: {sheet_title}", flush=True)

        worksheet.append_row([email, lat, lon, status, timestamp])
        print("✅ Row logged successfully", flush=True)

    except Exception as e:
        print("⚠️ Error logging attendance:", str(e), flush=True)
