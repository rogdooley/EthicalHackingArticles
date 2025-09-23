---
title: "Part 3 – Accepting Uploads (multipart/form-data)"
description: "Receive files via POST; save deterministically; return explicit results."
tags: [flask, uploads, multipart, http]
---

# Part 3 – Accepting Uploads (multipart/form-data)

## Goals
- Implement a POST route to accept `multipart/form-data` uploads.
- Save artifacts with predictable naming in a target directory.

## What You’ll Build
- `/upload` route that accepts one file field and persists it safely.

## Sections
- **Route Contract:** Validate presence of file → sanitize filename → save → return JSON summary.
- **Storage Layout:** Where to store (`save_dir`), naming patterns, collisions.
- **Security Considerations:** Don’t trust client filenames; avoid path traversal; size limits (conceptually).
- **Milestone:** curl POST works; file appears on disk with expected name.
- **Troubleshooting:** Missing `Content-Type`, wrong form field name, empty files.

A natural progression from allowing file downloads from the web server is to allow uploads. When performing assessments, there can be conditions where you need to transfer a file or files from a host to the attacking machine. Knowing how to create an instance of a server that can accept file uploads can be a nice skill to possess. I'll attempt to show how this is done using *Python* and *Flask*. 

In the interest of security, I'll define the the name of the file to be uploaded (`UPLOAD_FILE`), the directory where to store any uploaded files (`UPLOAD_DIRECTORY`) and the path to tack onto a url (`ROUTE`) . I've named these with rather pedestrian strings for the purpose of this example. If you ever need to do this in the wild, providing random names for any or all of these is easily accomplished. 

Apart from the initialization, I'll need to call on a few modules to help create this server. `Path` from *pathlib*  is used for file and directory handling. From *Flask*, import `Flask`, `request`, and `abort`. `Flask`is the method used to create the web application instance. `request` allows one to handle HTTP requests, and `abort` will allow the stoppage of a request handling and return the error code for a bad HTTP request (400).

```python
from pathlib import Path
from flask import Flask, request, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FILE = "my_file"
UPLOAD_DIRECTORY="./upload"
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=False)

```

```txt
POST /upload HTTP/1.1
Host: localhost:8888
Content-Type: multipart/form-data; boundary=----abc123
Content-Length: 253

------abc123
Content-Disposition: form-data; name="username"

roger
------abc123
Content-Disposition: form-data; name="file"; filename="payload.bin"
Content-Type: application/octet-stream

<binary bytes of payload.bin here>
------abc123--
```

As a slight aside, the `files` property is an immutable dictionary-like object from the `Werkzeug Library`. It's dictionary-like due to the object handling multiple values for the same key. So, under the hood, you would have something like the following:

```python
from werkzeug.datastructures import ImmutableMultiDict
form_data = ImmutableMultiDict([('filename','my_file'),('filename', 'another_file'), ('foo', 'bar')]) 
print(form_data.get('filename'))
print(form_data.getlist('filename'))
```

From a REPL:
```python
>>> print(form_data.get('filename'))
my_file
>>> print(form_data.getlist('filename'))
['my_file', 'another_file']
```

[Werkzeug FileStorage ](https://werkzeug.palletsprojects.com/en/stable/datastructures/#werkzeug.datastructures.FileStorage)

```python
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

```

```bash
curl -F "file=@my_file" http://127.0.0.1:8888/inspect-upload
```

![Under the hood for an upload](Images/Part3/02-inspect-file.png)

If you wanted to accept all files, you could change `file = ... return ...` to something like this:

```python

saved = []
for field_name, file in request.files.items():
    if file.filename:
        filename = secure_filename(file.filename)
        save_path = Path(UPLOAD_DIRECTORY) / filename
        file.save(save_path)
        saved.append({"field": field_name, "filename": filename})

return {"status": "success", "result": saved}, 200
```

```bash
curl -F "file=@payload.bin" http://127.0.0.1:8888/upload
```

```bash
curl -F "foo=@payload.bin" http://127.0.0.1:8888/upload
```

```bash
curl -F "alpha=@test1.txt" -F "beta=@test2.txt" http://127.0.0.1:8888/upload
```
## Exercises
- Upload multiple file types; verify extensions and sizes.
- Upload same filename twice; decide overwrite vs versioning.

## What’s Next
- Base64-encoded exfil via query/body for hostile transports.

### **Upload methods with** **curl**

| **Curl Flag**                                    | **Content-Type sent**              | **Body Structure**                                 | **Flask Accessor**                                        | **Typical Use Case**                 |
| ------------------------------------------------ | ---------------------------------- | -------------------------------------------------- | --------------------------------------------------------- | ------------------------------------ |
| -d "a=1&b=2"                                     | application/x-www-form-urlencoded  | a=1&b=2                                            | request.form["a"], request.form["b"]                      | Classic HTML forms                   |
| -d '{"x":1}' -H "Content-Type: application/json" | application/json                   | Raw JSON string                                    | request.json or request.get_json()                        | REST APIs, JSON payloads             |
| -F "file=@payload.bin"                           | multipart/form-data; boundary=...  | Multipart with boundaries, one part per field/file | Files: request.files["file"]Fields: request.form["field"] | Browser-style file uploads           |
| --data-binary @file.bin                          | application/octet-stream (default) | Raw file bytes                                     | request.data (raw bytes)                                  | Upload raw binary (no form encoding) |
| -T payload.bin                                   | application/octet-stream (default) | Raw file bytes                                     | request.data (if POST/PUT handler)                        | PUT/POST raw file, often for APIs    |



