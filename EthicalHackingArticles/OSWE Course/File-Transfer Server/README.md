---
title: "OSWE Toolkit: File-Transfer Server Series"
description: "Step-by-step learning module: building a minimal file-transfer server in Python with Flask, threading, and logging."
tags: [oswe, web-300, poc, flask, python]
---

# OSWE Toolkit: File-Transfer Server Series

This learning module documents the process of **building a custom file-transfer server** in Python.  
Instead of presenting the final class at once, each post adds one feature at a time. By the end, you’ll have a complete understanding of the code, the design choices, and how to use it in OSWE/WEB-300 style exploit development.

---

## Why This Series?

- **Deeper learning by building**: each article explains *how* and *why*, not just *what*.  
- **Reusable tooling**: the finished server is useful beyond the course — for PoCs, exfiltration, and payload hosting.  
- **Clarity in design**: threading, Flask, encoding, and callbacks are broken down into approachable steps.  

---

## Module Roadmap

1. **Part 1 – Why and Where to Begin**  
   Start with the motivation and build the most minimal Flask server.

2. **Part 2 – Serving a File (Download Route)**  
   Add the first real endpoint: deliver a payload via `send_file`.

3. **Part 3 – Accepting Uploads**  
   Introduce POST routes and file saving.

4. **Part 4 – Encoded Data and Exfiltration**  
   Handle base64-encoded input, useful for hostile transports.

5. **Part 5 – Limits, Callbacks, and Shutdown**  
   Add one-shot transfers, lifecycle control, and local shutdown.

6. **Part 6 – Logging and Observability**  
   Integrate with a logger for structured, report-ready output.

7. **Part 7 – Putting It All Together**  
   The final `FileTransferServer` class, ready for use in PoCs.

---

## How to Use This Module

- Draft and experiment inside **Obsidian**.  
- Push the same Markdown files to **GitBook** for polished publishing.  
- Run each code snippet locally as you go — every post builds toward the final result.  

---

## Next Step

Begin with [Part 1 – Why and Where to Begin](./part1.md).