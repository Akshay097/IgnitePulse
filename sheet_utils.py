import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ✅ Detect if running locally or on Render
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

def log_attendance(email, lat, lon, timestamp, status, altitude=None):
    if not client:
        print("⚠️ Skipping Google Sheet write: client not available", flush=True)
        return

    try:
        sheet_title = datetime.datetime.now().strftime("%m-%d-%Y")
        spreadsheet = client.open("Ignitemeetup Attendance")

        try:
            worksheet = spreadsheet.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            print(f"📄 Creating new sheet tab: {sheet_title}", flush=True)
            worksheet = spreadsheet.add_worksheet(title=sheet_title, rows="100", cols="10")
            worksheet.append_row(["Email", "Latitude", "Longitude", "Altitude", "Status", "Timestamp"])

        worksheet.append_row([email, lat, lon, altitude, status, timestamp])
        print("✅ Row logged successfully", flush=True)

    except Exception as e:
        import traceback
        print("⚠️ Error logging attendance:", flush=True)
        traceback.print_exc()
