---
title: "Part 4 – Encoded Data and Exfiltration (Base64)"
description: "Handle base64 payloads for environments where multipart isn’t feasible (XSS/SSRF)."
tags: [flask, base64, exfiltration, http, security]
---

# Part 4 – Encoded Data and Exfiltration (Base64)

## Goals
- Implement a GET-based exfil endpoint `GET /exfil?q=<b64>&filename=...`.
- Implement a POST-based JSON variant for encoded uploads.
- Decode safely; write artifacts predictably.

## What You’ll Build
- `/exfil` (GET) and `/upload-encoded` (POST JSON) with explicit outcomes.

## Sections
- **Why Base64:** Transport-compatibility in constrained vectors (XSS, SSRF).
- **Decoding Path:** Validate input → decode → write bytes → return 2xx/4xx.
- **Naming Strategy:** IP + timestamp fallback; reader-provided `filename`.
- **Error Handling:** Malformed base64 → explicit 400; missing params.
- **Milestone:** Exfil works with curl; artifacts reproducible on disk.
- **Security Notes:** Input sizes, log redaction, directory traversal avoidance.

## Exercises
- Attempt malformed input; confirm correct error and logs.
- Compare GET vs POST behavior and logging footprint.

## What’s Next
- Add one-shot limits, callbacks, and lifecycle shutdown.