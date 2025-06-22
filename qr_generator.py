import io
import qrcode
from flask import Blueprint, send_file, url_for, render_template, request
from datetime import datetime, timedelta
import pytz
import hashlib

qr_bp = Blueprint("qr", __name__)

# Global token store shared for validation
# You can optionally move this to a separate file/module for better design
class TokenStore:
    valid_token = None
    expires_at = None

def generate_new_token():
    atlantic = pytz.timezone("Canada/Atlantic")
    now = datetime.now(atlantic)
    rounded = now.replace(second=0, microsecond=0)  # exact minute
    token_base = rounded.strftime("%Y-%m-%d %H:%M")
    token = hashlib.sha256(token_base.encode()).hexdigest()[:10]

    TokenStore.valid_token = token
    TokenStore.expires_at = rounded + timedelta(minutes=1)
    print(f"🔐 Generated new QR token: {token} valid until {TokenStore.expires_at}", flush=True)
    return token

def get_current_token():
    atlantic = pytz.timezone("Canada/Atlantic")
    now = datetime.now(atlantic)

    if TokenStore.valid_token is None or now >= TokenStore.expires_at:
        return generate_new_token()
    return TokenStore.valid_token

@qr_bp.route("/generate_qr")
def generate_qr():
    base_url = url_for("index", _external=True)
    token = get_current_token()
    qr_data = f"{base_url}?token={token}"

    qr = qrcode.make(qr_data)
    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

@qr_bp.route("/qrcode")
def show_qr():
    atlantic = pytz.timezone("Canada/Atlantic")
    date_today = datetime.now(atlantic).strftime("%m-%d-%Y")
    url = request.host_url.strip("/")
    return render_template("qrcode.html", date=date_today, url=url)
