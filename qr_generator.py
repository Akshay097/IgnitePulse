import io
import qrcode
from flask import Blueprint, send_file, url_for, render_template, request
from datetime import datetime, timedelta
import pytz
import hashlib

qr_bp = Blueprint("qr", __name__)

# ✅ Timezone setup
atlantic = pytz.timezone("Canada/Atlantic")

# ✅ Clean token generation (no in-memory state)
def get_dynamic_token():
    """Always calculate token based on current minute (stateless)."""
    now = datetime.now(atlantic)
    rounded = now.replace(second=0, microsecond=0)
    token_base = rounded.strftime("%Y-%m-%d %H:%M")
    token = hashlib.sha256(token_base.encode()).hexdigest()[:10]
    return token

@qr_bp.route("/generate_qr")
def generate_qr():
    base_url = url_for("index", _external=True)
    token = get_dynamic_token()
    qr_data = f"{base_url}?token={token}"

    qr = qrcode.make(qr_data)
    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)

    print(f"🔐 Generated QR token: {token}", flush=True)
    return send_file(img_io, mimetype="image/png")

@qr_bp.route("/qrcode")
def show_qr():
    date_today = datetime.now(atlantic).strftime("%m-%d-%Y")
    url = request.host_url.strip("/")
    return render_template("qrcode.html", date=date_today, url=url)
