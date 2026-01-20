import sys
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from tracker import log_movement

def create_scanner_app(
    *,
    fixed_location: str,
    fixed_model: str = "-",
    fixed_substance: str = "-"
):
    app = Flask(__name__)

    HTML = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>QR Scanner</title>
      <script src="https://unpkg.com/html5-qrcode"></script>
    </head>
    <body>
      <h3>📷 Location: {{ location }}</h3>

      <div id="reader" style="width:300px"></div>

      <input id="status" placeholder="Status / Quantity" required>
      <button onclick="submit()">Submit</button>

      <script>
        let itemId = "";

        const qr = new Html5Qrcode("reader");
        qr.start(
          { facingMode: "environment" },
          { fps: 10, qrbox: 250 },
          decoded => {
            itemId = decoded;
            if (navigator.vibrate) navigator.vibrate(200);
            qr.stop();
          }
        );

        async function submit() {
          await fetch("/scan", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
              item_id: itemId,
              status: document.getElementById("status").value
            })
          });
          location.reload();
        }
      </script>
    </body>
    </html>
    """

    @app.route("/")
    def index():
        return render_template_string(HTML, location=fixed_location)

    @app.route("/scan", methods=["POST"])
    def scan():
        data = request.get_json(force=True)
        log_movement(
            item_id=data["item_id"],
            location=fixed_location,
            status=data["status"],
            model=fixed_model,
            substance=fixed_substance,
        )
        return jsonify(ok=True)

    return app
