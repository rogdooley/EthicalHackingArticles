---
title: "Part 5 – Limits, Callbacks, and Lifecycle Shutdown"
description: "Enforce one-shot/limited transfers; trigger hooks; stop the server cleanly."
tags: [threading, lifecycle, callbacks, limits]
---

# Part 5 – Limits, Callbacks, and Lifecycle Shutdown

## Learning Objectives
- Enforce one-shot or limited-use transfers and signal “limit reached” via HTTP.
- Wire a callback that triggers the next stage of an exploit chain.
- Implement a deterministic shutdown watcher and a loopback-only admin stop.

## Goals
- Add a transfer counter and configurable `limit`.
- Introduce `on_transfer(path, count)` callback to chain stages.
- Implement an automatic shutdown watcher.
- Add a loopback-only admin shutdown endpoint.

## Key Terms
- **410 Gone:** Resource intentionally unavailable (e.g., transfer limit reached).
- **Loopback:** Requests originating from the same host (`127.0.0.1`).
- **Watcher Thread:** Background thread monitoring state to trigger shutdown.

## What You’ll Build
- Transfer counting shared across routes.
- A background thread that stops the server when `count >= limit`.
- `POST /__shutdown` restricted to `127.0.0.1`.

## Sections
- **Counting Model:** Increment on success; define “a transfer”.
- **Callbacks:** Where/when to call; exception handling; idempotency.
- **Shutdown Watcher:** Thread polling vs event-driven; clean resource release.
- **Admin Endpoint:** Restrict by `remote_addr`, choose method (POST).
- **HTTP Semantics:** `410 Gone` when limit reached; rationale.
- **Milestone:** Single successful transfer → server stops deterministically.

## Exercises
- Set `limit=1` and verify shutdown; set `limit=2` and verify `410` on the third attempt.
- Simulate callback failure and ensure server stability.

## What’s Next
- Integrate consistent logging and status markers across all routes.