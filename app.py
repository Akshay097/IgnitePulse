from flask import Flask, render_template, request, jsonify
import json
import datetime
import math
import pytz  # ✅ timezone for Atlantic
from sheet_utils import log_attendance
from qr_generator import qr_bp  # ✅ import the blueprint

app = Flask(__name__)
app.register_blueprint(qr_bp)  # ✅ attach the QR routes to main app

# Load whitelist (approved emails)
with open("whitelist.json", "r") as f:
    WHITELIST = set(json.load(f))

# Set your office geolocation (example: Halifax, NS)
OFFICE_LAT = 44.72338559753693
OFFICE_LON = -63.6954247294425
GEOFENCE_RADIUS_KM = 0.01  # 150 meters

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    email = data.get("email")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))

    # ✅ Handle altitude safely
    alt = data.get("altitude")
    if alt is not None:
        try:
            alt = float(alt)
        except ValueError:
            alt = None

    if not email or not lat or not lon:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    if email not in WHITELIST:
        print(f"❌ Unauthorized email: {email} — blocked", flush=True)
        return jsonify({"status": "error", "message": "Unauthorized email"}), 403

    # ✅ This line must not be indented under the above if
    distance = haversine(lat, lon, OFFICE_LAT, OFFICE_LON)

    # Use Atlantic Daylight Time
    atlantic = pytz.timezone("Canada/Atlantic")
    now = datetime.datetime.now(atlantic).strftime("%Y-%m-%d %H:%M:%S")

    print(f"📏 Calculated distance: {distance:.4f} km", flush=True)
    print(f"📐 Altitude received: {alt}", flush=True)

    # Floor validation range (e.g. 5th floor)
    ALT_MIN = 52
    ALT_MAX = 62

    # 🧠 Flexible logic
    if alt is None:
        print("⚠️ No altitude — falling back to geofence only", flush=True)
        log_attendance(email, lat, lon, now, "Absent", alt)
        return jsonify({
            "status": "warning",
            "message": "Please contact your Coach or Ignite Audit Team member immediately, if you're in the office. Marked Absent."
        })

    if distance > GEOFENCE_RADIUS_KM or not (ALT_MIN <= alt <= ALT_MAX):
        print("🚫 Outside allowed location/altitude — Absent", flush=True)
        log_attendance(email, lat, lon, now, "Absent", alt)
        return jsonify({
            "status": "warning",
            "message": "You are outside the allowed area or floor. Marked Absent."
        })

    # ✅ Both conditions passed
    print("✅ Inside geofence and altitude range — Present", flush=True)
    log_attendance(email, lat, lon, now, "Present", alt)
    return jsonify({"status": "success", "message": "Attendance marked!"})

@app.route("/qrcode")
def show_qr():
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    qr_filename = f"qr_{today}.png"
    qr_path = f"/static/{qr_filename}"
    return render_template("qrcode.html", today=today, qr_path=qr_path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
