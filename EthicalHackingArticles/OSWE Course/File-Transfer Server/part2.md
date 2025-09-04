---
title: "Building a Minimal File-Transfer Server: Part 2 – Serving a File (Download Route)"
description: "Add the first real endpoint: deliver a payload reliably and predictably, with and without Flask's send_file helper."
tags: [oswe, web-300, poc, flask, python]
---

# Part 2 – Serving a File (Download Route)

In this part, we add the first real capability: **serve a file on demand** at a dedicated route. This lays the foundation for payload delivery in exploit chains.

We’ll build a small, runnable example first, then discuss behavior and trade-offs. 

---

## Minimal Download Server (single route)

Create `download_server.py`:

```python
from pathlib import Path
from flask import Flask, send_file, abort

app = Flask(__name__)

# Configuration for this tutorial step
PAYLOAD_PATH = Path("payload.bin")
ROUTE = "/download"  # In later parts we'll randomize this for stealth

@app.route(ROUTE, methods=["GET"])
def handle_download():
    # 1) Validate file existence to return an explicit error early
    if not PAYLOAD_PATH.exists():
        # 404 makes the failure clear for your notes/artifacts
        abort(404)

    # 2) Return the file as an attachment (Content-Disposition: attachment)
    #    This is useful when you want the client to save rather than render inline.
    return send_file(PAYLOAD_PATH, as_attachment=True)

if __name__ == "__main__":
    # Bind to localhost for safety during development
    app.run(host="127.0.0.1", port=8888, debug=False)

```

Expected behavior:

- If payload.bin exists, Flask returns 200 OK with the file bytes and an attachment disposition.
    
- If not, the server returns 404 Not Found.
    

---

## **Line-by-line reasoning**

- send_file(PAYLOAD_PATH, as_attachment=True)
    
    - Sets Content-Disposition: attachment; filename="payload.bin" which nudges browsers/clients to download rather than render.
        
    - Automatically sets Content-Length, Content-Type (best-effort), and handles range requests where applicable.
        
    
- abort(404)
    
    - Explicit failure mode improves observability in your logs and reports.
        
    - In later parts, we’ll add structured logging before aborting.
        
    
- ROUTE = "/download"
    
    - Fixed here for simplicity. In production tooling you’ll generate a randomized route (e.g., "/" + secrets.token_urlsafe(6)) to reduce guessability.
        
    

---

## **Operational notes for PoCs**

- **Determinism**: Always check that the file exists and is readable before responding.
- **Content-Disposition**: Use as_attachment=True for payloads you expect to be saved to disk.
- **Content-Type**: send_file infers from the filename. For ambiguous payloads, specify mimetype="application/octet-stream" explicitly.

  

Example:
```python
return send_file(PAYLOAD_PATH, as_attachment=True, mimetype="application/octet-stream")
```
