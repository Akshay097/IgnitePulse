import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Dynamically choose the right path for credentials
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
    client = None  # Important! Prevent crash later

SHEET_NAME = "Ignitemeetup_Attendance"

def log_attendance(email, lat, lon, timestamp, status):
    try:
        if client is None:
            print("⚠️ Skipping Google Sheet write: client not available", flush=True)
            return

        print(f"📥 Logging attendance for: {email}", flush=True)
        print(f"📍 Location: {lat}, {lon} | Status: {status} | Time: {timestamp}", flush=True)

        sheet_name = timestamp.split(" ")[0]
        sheet_tab = datetime.datetime.strptime(sheet_name, "%Y-%m-%d").strftime("%m-%d-%Y")
        print(f"📄 Using sheet tab: {sheet_tab}", flush=True)

        try:
            worksheet = client.open("Ignitemeetup-Attendance").worksheet(sheet_tab)
        except gspread.exceptions.WorksheetNotFound:
            print("➕ Sheet tab not found — creating new one", flush=True)
            template = client.open("Ignitemeetup-Attendance").sheet1
            worksheet = client.open("Ignitemeetup-Attendance").add_worksheet(title=sheet_tab, rows="100", cols="6")
            worksheet.insert_row(template.row_values(1), index=1)

        worksheet.append_row([email, lat, lon, timestamp, status])
        print("✅ Row logged successfully", flush=True)

    except Exception as e:
        print("⚠️ Error logging attendance:", str(e), flush=True)

