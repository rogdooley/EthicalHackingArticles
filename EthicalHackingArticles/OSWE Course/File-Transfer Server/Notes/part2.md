---
title: "Part 2 – Serving a File (Download Route)"
description: "Add a controlled download endpoint for payload delivery; discuss headers and error handling."
tags: [flask, send_file, http, payload-delivery]
---

# Part 2 – Serving a File (Download Route)

## Learning Objectives
- Implement a GET route that returns a file with explicit error handling.
- Explain the effects of `Content-Disposition` and `Content-Type` in payload delivery.
- Compare Flask `send_file` vs manual streaming approaches.

## Goals
- Implement a `/download` (later randomized) route that returns a file.
- Understand `Content-Disposition`, `Content-Type`, and explicit 404 handling.

## Key Terms
- **Content-Disposition:** HTTP header indicating inline vs attachment; controls filename.
- **Content-Type (MIME):** Declares media type (e.g., `application/octet-stream`).
- **404 Not Found:** Explicit error when the payload file doesn’t exist.

## What You’ll Build
- A download handler using `send_file`, plus a brief alt-path using manual streaming.

## Sections
- **Route Contract:** Validate existence → return file → explicit errors.
- **Headers:** Attachment vs inline; mimetype defaults; size and range handling.
- **Operational Notes:** Deterministic filenames for reproducibility.
- **Milestone:** File download succeeds; 404 when missing.
- **Troubleshooting:** Permissions, relative vs absolute paths, large files.

## Exercises
- Change filename and observe `Content-Disposition`.
- Force `mimetype="application/octet-stream"` and compare behavior.

## What’s Next
- Introduce uploads via `multipart/form-data`.