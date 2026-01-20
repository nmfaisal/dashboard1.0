from scanner_base import create_scanner_app

app = create_scanner_app(
    fixed_location="Office",
    fixed_model= "Model A",
    fixed_substance= "Substance A"
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context="adhoc")
