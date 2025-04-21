import qrcode
import datetime

# Base URL of your deployed app
base_url = "https://ignitemeetup.onrender.com"

# Generate today's date string
today = datetime.datetime.now().strftime("%m-%d-%Y")

# Final link to embed in QR
attendance_url = f"{base_url}?date={today}"

# Create QR code
qr = qrcode.make(attendance_url)

# Save it as image
qr_file = f"static/qr_{today}.png"
qr.save(qr_file)

print(f"✅ QR Code generated and saved as {qr_file}")
print(f"📎 Link embedded: {attendance_url}")
