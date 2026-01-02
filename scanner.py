from tracker import log_movement

while True:
    item_id = input("Scan barcode / QR (or 'q' to quit): ").strip()
    if item_id.lower() == "q":
        break

    location = input("Location: ").strip()
    status = input("Status: ").strip()

    log = log_movement(item_id, location, status)
    print("Logged:", log)
