import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)

# Authorize the client
client = gspread.authorize(creds)

# Open your Google Sheet (replace this with your actual sheet name)
SHEET_NAME = "Ignitemeetup_Attendance"
worksheet = client.open(SHEET_NAME).sheet1

def log_attendance(email, latitude, longitude, timestamp, status):
    date_sheet_name = datetime.datetime.now().strftime("%m-%d-%Y")

    try:
        worksheet = client.open(SHEET_NAME).worksheet(date_sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = client.open(SHEET_NAME).add_worksheet(title=date_sheet_name, rows="100", cols="10")
        worksheet.append_row(["Email", "Latitude", "Longitude", "Timestamp", "Status"])

    worksheet.append_row([email, latitude, longitude, timestamp, status])

