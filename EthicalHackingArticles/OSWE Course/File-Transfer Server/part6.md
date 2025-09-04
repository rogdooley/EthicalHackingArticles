---
title: "Part 6 – Logging and Observability"
description: "Integrate structured, consistent logging (console/file); make outputs report-ready."
tags: [logging, observability, reporting]
---

# Part 6 – Logging and Observability

## Goals
- Integrate a lightweight logger with severity levels and consistent prefixes.
- Optionally support dual sinks (stdout + file).
- Capture timestamps and key metadata (route, remote IP, filename, size).

## What You’ll Build
- Logging calls in each route and in lifecycle transitions.
- A simple, uniform log format tailored to PoC reporting.

## Sections
- **Log Taxonomy:** info, success, warn, error, status.
- **Placement:** Before/after critical actions; include counters and limits.
- **Artifacts:** Where to write logs; filename pattern; rotation considerations.
- **Milestone:** Logs show a clear timeline of actions for a single run.

## Exercises
- Run a full cycle (download or exfil) and capture a clean log excerpt for notes.
- Add minimal correlation IDs if chaining multiple tools.

## What’s Next
- Assemble the parts into the final `FileTransferServer` class with ergonomic configuration.