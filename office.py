from tracker import log_movement
from pathlib import Path
from datetime import datetime
import json
import sys

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import qrcode
import os

DEBUG = False

# ==============================
# EXE-SAFE BASE DIR
# ==============================
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

COUNTER_FILE = BASE_DIR / "office_counter.json"
PDF_DIR = BASE_DIR / "srv/pdf"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# GENERATE DAILY ITEM ID
# ==============================
def generate_item_id():
    today_str = datetime.now().strftime("%y%m%d")

    if COUNTER_FILE.exists():
        with open(COUNTER_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"date": today_str, "counter": 0}

    # Reset counter if new day
    if data["date"] != today_str:
        data = {"date": today_str, "counter": 0}

    data["counter"] += 1

    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)

    return f"NM{today_str}_{data['counter']:03d}"


# def create_label_pdf(item_id, model, substance, quantity):
#     pdf_path = PDF_DIR / f"{item_id}.pdf"

#     styles = getSampleStyleSheet()
#     story = []

#     # ===== TEXT INFO =====
#     story.append(Paragraph(f"<b>Item ID:</b> {item_id}", styles["Title"]))
#     story.append(Spacer(1, 12))

#     story.append(Paragraph(f"<b>Model:</b> {model}", styles["Normal"]))
#     story.append(Paragraph(f"<b>Substance:</b> {substance}", styles["Normal"]))
#     story.append(Paragraph(f"<b>Quantity:</b> {quantity}", styles["Normal"]))

#     story.append(Spacer(1, 24))

#     # ===== GENERATE QR CODE =====
#     qr_img_path = PDF_DIR / f"{item_id}_qr.png"

#     qr = qrcode.make(item_id)
#     qr.save(qr_img_path)

#     # ===== ADD QR IMAGE TO PDF =====
#     story.append(Paragraph("<b>Scan for Tracking</b>", styles["Normal"]))
#     story.append(Spacer(1, 12))
#     story.append(Image(str(qr_img_path), width=120, height=120))

#     # ===== BUILD PDF =====
#     doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
#     doc.build(story)

#     return pdf_path

def generate_pdf(item_id, model, substance, quantity, location):
    pdf_path = PDF_DIR / f"{item_id}.pdf"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Production Tracking Label", styles["Title"]))
    story.append(Spacer(1, 12))

    # =========================
    # TABLE CONTENT
    # =========================
    data = [
        ["QR Code", item_id],
        ["Model", model],
        # ["Substance", substance],
        # ["Quantity", quantity],
        # ["Location", location],
        # ["Timestamp", timestamp],
    ]

    table = Table(data, colWidths=[140, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # =========================
    # QR CODE GENERATION
    # =========================
    qr_img_path = f"{item_id}_qr.png"

    qr = qrcode.make(item_id)
    qr.save(qr_img_path)

    story.append(Paragraph("Scan for Tracking", styles["Heading3"]))
    story.append(Spacer(1, 10))
    story.append(Image(qr_img_path, width=240, height=240))

    # =========================
    # BUILD PDF
    # =========================
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    doc.build(story)

    # =========================
    # DELETE TEMP QR IMAGE
    # =========================
    if os.path.exists(qr_img_path):
        os.remove(qr_img_path)

    return pdf_path

# ==============================
# OFFICE SCANNER LOOP
# ==============================
while True:
    item_id = generate_item_id()
    print(f"\n🆔 Generated QR Code: {item_id}")

    model = input("Model: ").strip()
    substance = input("Substance: ").strip()
    status = input("Quantity: ").strip()

    location = "Office"
    log = log_movement(item_id, location, status, model, substance)
    if DEBUG:
        print("✅ Logged:", log)
    print("✅ Information saved.")


    # 🧾 Create PDF FIRST
    # pdf_file = create_label_pdf(item_id, model, substance, status)
    pdf_file = generate_pdf(item_id, model, substance, status, location)
    if DEBUG:
        print(f"PDF saved: {pdf_file}")
    print("✅ PDF file saved. Open to print.")

    cont = input("\nPress ENTER for next item or type 'q' to quit: ").strip().lower()
    if cont == "q":
        break
