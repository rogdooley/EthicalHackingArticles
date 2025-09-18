from pathlib import Path
from flask import Flask, request, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FILE = "my_file"
UPLOAD_DIRECTORY="./upload2"
ROUTE="/upload"

Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

@app.route(ROUTE, methods=["POST"])
def handle_upload():
    if "file" not in request.files:
        abort(400, description="No file part in request")

    file = request.files["file"]

    if file.filename == "":
        abort(400, description="No file selected")
	
    filename = secure_filename(file.filename)
    save_path = Path(UPLOAD_DIRECTORY) / filename
    file.save(save_path)
	
    return { "status": "sucess", "result": f"{filename} saved to {save_path}"}, 200


@app.route("/inspect-upload", methods=["POST"])
def inspect_upload():
    if "file" not in request.files:
        abort(400, "No file in request")

    f = request.files["file"]  # Werkzeug FileStorage

    # Basic metadata
    content_type = f.mimetype            
    filename = f.filename
    content_length = request.content_length  

    first_bytes = f.stream.read(10)
    try:
        f.stream.seek(0)
    except (AttributeError, OSError):
        pass

    # Pick a few useful headers instead of dumping everything
    content_type_header = request.headers.get("Content-Type")
    user_agent = request.headers.get("User-Agent", "<none>")

    # Log/print (avoid in production — here for teaching/debugging)
    print(f"Content Type (mimetype): {content_type}")
    print(f"Filename: {filename}")
    print(f"Request Content-Length: {content_length}")
    print(f"Content-Type header: {content_type_header}")
    print(f"User-Agent: {user_agent}")
    print(f"First 10 bytes (hex): {first_bytes.hex() if first_bytes else '<empty>'}")

    return {
        "filename": filename,
        "mimetype": content_type,
        "first_bytes": first_bytes.hex() if first_bytes else None
    }, 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=False)
