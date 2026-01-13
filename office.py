from tracker import log_movement

while True:
    item_id = input("Scan barcode / QR (or 'q' to quit): ").strip()
    if item_id.lower() == "q":
        break

    location = "Office" 
    # status = "processing"
    model = input("Model/Part No: ").strip()
    substance = input("Raw Miri Substance: ").strip()
    status = input("Quantity: ").strip()

    log = log_movement(item_id, location, status, model, substance)
    print("Logged:", log)
