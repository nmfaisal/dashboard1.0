import sys
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from tracker import log_movement

# ==========================
# EXE-SAFE BASE DIRECTORY
# ==========================
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

TRACE_LOG = BASE_DIR / "srv" / "data" / "trace_log.csv"
TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)

# ==========================
# FIXED BACKEND VALUES
# ==========================
FIXED_LOCATION = "FG"
FIXED_MODEL = "-"
FIXED_SUBSTANCE = "-"

# ==========================
# FLASK APP
# ==========================
app = Flask(__name__)

# ==========================
# MOBILE SCANNER PAGE
# ==========================
HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mobile QR Scanner</title>

  <!-- QR SCANNER LIB -->
  <script src="https://unpkg.com/html5-qrcode"></script>

  <style>
    body { font-family: Arial; padding: 20px; }
    input, button {
      font-size: 18px;
      width: 100%;
      padding: 10px;
      margin-top: 10px;
    }
    button {
      background-color: #2e86de;
      color: white;
      border: none;
    }
  </style>
</head>

<body>
  <h2>📷 Mobile QR Scanner</h2>

  <!-- CAMERA PREVIEW -->
  <div id="reader" style="width:300px;"></div>

  <!-- USER FORM -->
  <form id="form">
    <input id="item_id" placeholder="Item ID" required readonly>

    <input id="status" placeholder="Status / Quantity" required>

    <button type="submit">Submit</button>
  </form>

  <p id="msg"></p>

<script>
  const itemInput = document.getElementById("item_id");
  const statusInput = document.getElementById("status");
  const msg = document.getElementById("msg");

  const qr = new Html5Qrcode("reader");

  function startScanner() {
    qr.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      decoded => {
        itemInput.value = decoded;

        // 📳 vibration feedback
        if (navigator.vibrate) navigator.vibrate(200);

        // stop scanning after successful scan
        qr.stop();
      }
    ).catch(err => {
      msg.innerText = "Camera error: " + err;
    });
  }

  // AUTO START CAMERA ON LOAD
  startScanner();

  document.getElementById("form").onsubmit = async (e) => {
    e.preventDefault();

    const res = await fetch("/scan", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        item_id: itemInput.value,
        status: statusInput.value
      })
    });

    if (res.ok) {
      msg.innerText = "✔ Saved";
      itemInput.value = "";
      statusInput.value = "";

      // restart scanner for next item
      startScanner();
    } else {
      msg.innerText = "❌ Error saving data";
    }
  };
</script>

</body>
</html>
"""

# ==========================
# ROUTES
# ==========================
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json(force=True)

    log_movement(
        item_id=data.get("item_id", ""),
        location=FIXED_LOCATION,
        status=data.get("status", ""),
        model=FIXED_MODEL,
        substance=FIXED_SUBSTANCE
    )

    return jsonify(ok=True)

# ==========================
# START SERVER (HTTPS ENABLED)
# ==========================
if __name__ == "__main__":
    # ssl_context="adhoc" enables HTTPS with self-signed cert
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context="adhoc"
    )
