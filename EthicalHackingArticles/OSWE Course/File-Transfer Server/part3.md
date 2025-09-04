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

## Exercises
- Upload multiple file types; verify extensions and sizes.
- Upload same filename twice; decide overwrite vs versioning.

## What’s Next
- Base64-encoded exfil via query/body for hostile transports.