from pathlib import Path
from flask import Flask, request, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FILE = "my_file"
UPLOAD_DIRECTORY="/tmp"
ROUTE="upload"

Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

@app.route(ROUTE, methods=["POST"])
def handle_upload()
	file = request.files[UPLOAD_FILE]
	
	if "file" not in request.files:
	    abort(400, description="No file part in request")
	
	file = request.files["file"]

	if file.filename == "":
	    abort(400, description="No file selected")
	
	filename = secure_filename(file.filename)
	save_path = Path(UPLOAD_DIRECTORY) / filename
	file.save(save_path)
	
	return { "status": "sucess", "result": f"{filename} saved to {save_path}"}, 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=False)
