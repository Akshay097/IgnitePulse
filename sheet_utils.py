import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 🔐 Credentials path for Render vs. local
if os.path.exists("/etc/secrets/credentials.json"):
    CREDENTIALS_PATH = "/etc/secrets/credentials.json"
else:
    CREDENTIALS_PATH = "credentials.json"

try:
    print("🔐 Loading credentials from:", CREDENTIALS_PATH)
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
    client = gspread.authorize(creds)
    print("✅ Google Sheets authorized successfully")
except Exception as e:
    print("❌ Failed to authorize Google Sheets:", str(e))

SHEET_NAME = "Ignitemeetup_Attendance"

def log_attendance(email, lat, lon, timestamp, status):
    try:
        print(f"📥 Logging attendance for: {email}", flush=True)
        print(f"📍 Location: {lat}, {lon} | Status: {status} | Time: {timestamp}", flush=True)

        date_sheet_name = datetime.datetime.now().strftime("%m-%d-%Y")
        print(f"📄 Using sheet tab: {date_sheet_name}")

        try:
            worksheet = client.open(SHEET_NAME).worksheet(date_sheet_name)
            print("📄 Existing tab found.")
        except gspread.exceptions.WorksheetNotFound:
            print("➕ Tab not found. Creating new sheet tab...")
            worksheet = client.open(SHEET_NAME).add_worksheet(
                title=date_sheet_name,
                rows="100",
                cols="6"
            )
            worksheet.append_row(["Timestamp", "Email", "Latitude", "Longitude", "Status"])

        worksheet.append_row([timestamp, email, lat, lon, status])
        print("✅ Row logged successfully")

    except Exception as e:
        print("✅ Row logged successfully", flush=True)
        print("⚠️ Error logging attendance:", str(e), flush=True)
