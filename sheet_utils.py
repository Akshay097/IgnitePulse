import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set scope for Google Sheets and Drive API
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ✅ Dynamic path for credentials (local or Render)
if os.path.exists("/etc/secrets/credentials.json"):
    CREDENTIALS_PATH = "/etc/secrets/credentials.json"
else:
    CREDENTIALS_PATH = "credentials.json"

# Load credentials
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
client = gspread.authorize(creds)

# Google Sheet name
SHEET_NAME = "Ignitemeetup_Attendance"

def log_attendance(email, lat, lon, timestamp, status):
    try:
        date_sheet_name = datetime.datetime.now().strftime("%m-%d-%Y")

        # Try to open the sheet, or create a new one if not exists
        try:
            worksheet = client.open(SHEET_NAME).worksheet(date_sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = client.open(SHEET_NAME).add_worksheet(title=date_sheet_name, rows="100", cols="6")
            worksheet.append_row(["Timestamp", "Email", "Latitude", "Longitude", "Status"])

        worksheet.append_row([timestamp, email, lat, lon, status])
    except Exception as e:
        print("Error logging attendance:", str(e))
