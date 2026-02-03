from scanner_base import create_scanner_app

app = create_scanner_app(
    fixed_location="FG"
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, ssl_context="adhoc")
