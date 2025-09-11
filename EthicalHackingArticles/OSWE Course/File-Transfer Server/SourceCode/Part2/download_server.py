from pathlib import Path
from flask import Flask, send_file, abort

app = Flask(__name__)

PAYLOAD_PATH = Path("payload.bin")
ROUTE = "/download"  # In later parts we'll randomize this for stealth

@app.route(ROUTE, methods=["GET"])
def handle_download():
    if not PAYLOAD_PATH.exists():
        abort(404)
    return send_file(PAYLOAD_PATH, as_attachment=True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=False)
