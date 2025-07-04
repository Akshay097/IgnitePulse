from flask import Flask, render_template, request, jsonify
import json
import datetime
import math
import pytz
import os

from sheet_utils import log_attendance, log_audit, check_device_binding, bind_device
from qr_generator import qr_bp, get_dynamic_token  
from device_utils import get_device_id_from_request
from ip_logger import log_user_ip, is_ip_suspicious, get_client_ip
from audit_logger import log_audit_entry, detect_device_sharing, detect_multiple_ips

app = Flask(__name__)
app.register_blueprint(qr_bp)

with open("whitelist.json", "r") as f:
    WHITELIST = set(json.load(f))

# Office Configurations
OFFICE_LAT = 44.72338559753693
OFFICE_LON = -63.6954247294425
GEOFENCE_RADIUS_KM = 0.07

# Utility
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
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
    device_id = data.get("device_id")
    token = data.get("token")
    user_ip = get_client_ip(request)

    # ✅ Validate input fields
    if not email or not lat or not lon or not device_id or not token:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    if email not in WHITELIST:
        return jsonify({"status": "error", "message": "Unauthorized email"}), 403

    # ✅ Validate Token freshness
    valid_token = get_dynamic_token()
    if token != valid_token:
        return jsonify({"status": "error", "message": "QR Code expired. Please scan again."}), 403

    # ✅ Timezone aware timestamp
    atlantic = pytz.timezone("Canada/Atlantic")
    now_dt = datetime.datetime.now(atlantic)
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    # 🔍 Log IP and detect anomalies
    log_user_ip(email, user_ip)
    if is_ip_suspicious(email, user_ip):
        print(f"⚠️ Suspicious IP detected for {email} at {user_ip}")

    if detect_device_sharing(device_id, email):
        print(f"⚠️ Device sharing detected for {device_id}")
    if detect_multiple_ips(email, user_ip):
        print(f"⚠️ Multiple IPs detected for {email}")

    # 🛡️ Prevent duplicate submissions per device per day
    already_submitted = log_audit(email, now_str, user_ip, device_id, lat, lon)
    if already_submitted:
        return jsonify({"status": "warning", "message": "Attendance already marked from this device today."})

    # 🔐 Device binding on first use
    bound = check_device_binding(email, device_id)
    if not bound:
        bind_device(email, device_id)
        print(f"🔗 Bound new device for: {email}")

    # 📍 Geofencing check
    distance = haversine(lat, lon, OFFICE_LAT, OFFICE_LON)
    print(f"📏 User distance from office: {distance:.2f} km")

    if distance > GEOFENCE_RADIUS_KM:
        log_attendance(email, lat, lon, now_str, "Absent", device_id, user_ip, "Outside geofence")
        log_audit_entry(email, now_str, device_id, user_ip, "Absent", reason="Outside geofence")
        return jsonify({"status": "warning", "message": "Outside geofence. Marked Absent."})

    # ✅ All checks passed
    log_attendance(email, lat, lon, now_str, "Present", device_id, user_ip)
    log_audit_entry(email, now_str, device_id, user_ip, "Present")
    return jsonify({"status": "success", "message": "Attendance marked!"})

@app.route("/qrcode")
def show_qr():
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    return render_template("qrcode.html", date=today)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
