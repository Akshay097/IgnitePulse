import io
import qrcode
from flask import Blueprint, send_file, url_for, render_template, request
from datetime import datetime
import pytz
import hashlib

qr_bp = Blueprint("qr", __name__)

def get_dynamic_token():
    """Generate a time-based token that changes every 1 minute."""
    atlantic = pytz.timezone("Canada/Atlantic")
    now = datetime.now(atlantic)
    token_base = now.strftime("%Y-%m-%d %H:%M")
    token = hashlib.sha256(token_base.encode()).hexdigest()[:10]  # First 10 characters of hash
    return token

@qr_bp.route("/generate_qr")
def generate_qr():
    base_url = url_for("index", _external=True)
    token = get_dynamic_token()
    qr_data = f"{base_url}?token={token}"  # Token embedded in URL

    qr = qrcode.make(qr_data)
    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)

    print(f"🔁 Generated QR with token: {token}", flush=True)
    return send_file(img_io, mimetype="image/png")

@qr_bp.route("/qrcode")
def show_qr():
    url = request.host_url.strip("/")
    atlantic = pytz.timezone("Canada/Atlantic")
    date_today = datetime.now(atlantic).strftime("%m-%d-%Y")
    return render_template("qrcode.html", date=date_today, url=url)
