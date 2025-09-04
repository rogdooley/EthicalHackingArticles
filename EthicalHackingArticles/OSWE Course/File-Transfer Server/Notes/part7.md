---
title: "Part 7 – Putting It All Together (Final Class + Exploit Skeleton Integration)"
description: "Assemble the full FileTransferServer; map it into an exploit skeleton with a standardized artifacts layout."
tags: [flask, threading, design, ergonomics, integration]
---

# Part 7 – Putting It All Together (Final Class + Exploit Skeleton Integration)

## Learning Objectives
- Assemble a cohesive `FileTransferServer` with clear constructor parameters and defaults.
- Integrate the server into an exploit skeleton using callbacks and lifecycle hooks.
- Standardize artifacts layout and naming across tools for repeatable workflows.

## Goals
- Merge features into a cohesive `FileTransferServer`.
- Provide a clean constructor with sensible defaults.
- Document public methods and calling conventions.
- Integrate with a standard artifacts/logs directory layout.

## Key Terms
- **Artifacts Root:** Top directory for all run outputs and logs.
- **Run ID:** Time-based identifier to group artifacts from a single execution.
- **Lifecycle Hooks:** Explicit points to start/stop services or record evidence.

## What You’ll Build
- Final class with:
  - Configurable `file_path`, `save_dir`, `direction` (download/upload/both).
  - `limit`, `encoded` mode, randomized `route`, `port`.
  - Optional HTML landing page.
  - `on_transfer` callback, `start()`/`stop()`, `__repr__`.
  - Logging wired throughout.
- Integration pattern with a canonical artifacts layout.

## Standard Artifacts Layout
```text
ARTIFACTS_ROOT/
└── oswe-file-transfer/
    └── {RUN_ID}/
        ├── logs/
        │   └── transfer.log
        ├── exfil/
        │   └── {client_ip}_{utc-ts}[_{hint}].bin
        ├── uploads/
        │   └── {sanitized-filename}[.{n}]
        ├── downloads/
        │   └── payload-metadata.json
        └── meta/
            ├── run.json        # config snapshot (port, route, direction, limit, encoded)
            └── timeline.json   # key events with timestamps