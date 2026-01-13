from tracker import log_movement

while True:
    item_id = input("Scan barcode / QR (or 'q' to quit): ").strip()
    if item_id.lower() == "q":
        break

    location = "FG" 
    # status = "processing"
    status = input("Quantity: ").strip()
    model = "-"
    substance = "-"

    log = log_movement(item_id, location, status, model, substance)
    print("Logged:", log)
