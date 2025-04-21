import io
import qrcode
from flask import Blueprint, send_file, url_for, render_template, request  # ✅ important

from datetime import datetime

qr_bp = Blueprint("qr", __name__)

# Route to generate the actual QR code image
@qr_bp.route("/generate_qr")
def generate_qr():
    qr_data = url_for("index", _external=True)
    qr = qrcode.make(qr_data)

    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


# Route to render the QR code page
@qr_bp.route("/qrcode")
def show_qr():
    url = request.host_url.strip("/")  
    date_today = datetime.now().strftime("%m-%d-%Y")  
    print(f"🧪 Date passed to template: {date_today}", flush=True)  # ✅ Debug
    return render_template("qrcode.html", date=date_today, url=url)

