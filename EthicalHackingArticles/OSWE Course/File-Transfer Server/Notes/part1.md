---
title: "Building a Minimal File-Transfer Server: Part 1 – Why and Where to Begin"
description: "Motivation, scope, and the smallest Flask app we’ll grow into a file-transfer microservice."
tags: [oswe, web-300, flask, python, learning-module]
---

# Part 1 – Why and Where to Begin

## Learning Objectives
- Articulate why ad-hoc HTTP servers fall short for OSWE-style exploit development.
- Describe the target capabilities of a minimal file-transfer service.
- Stand up a minimal Flask app and verify basic routing locally.

## Goals
- Establish the problem space (payload hosting, exfil, teardown).
- Define constraints relevant to OSWE/WEB-300 labs.
- Stand up the smallest viable Flask app as a foundation.

## Key Terms
- **Bind Address:** Network interface the server listens on (e.g., `127.0.0.1` vs `0.0.0.0`).
- **Route:** A URL path handled by a server function (e.g., `/download`).
- **Artifact:** Any saved output from a run (files, logs, timestamps).

## Prerequisites
- Python 3.12+, virtual environment basics.
- High-level HTTP request/response understanding.

## What You’ll Build
- A minimal Flask server that responds at `/`.

## Sections
- **Context:** Why ad-hoc servers fall short for exploit chains.
- **Design Principles:** Minimal surface area, explicit failure codes, short lifecycle.
- **Architecture Preview:** Routes we’ll add later (download, upload, exfil, admin).
- **Milestone:** Minimal Flask app boots and responds.
- **Sanity Checks:** curl `GET /`, verify port binding, dev vs bind-all.
- **Pitfalls:** Firewalls, port-in-use, Python path issues.
- **What’s Next:** Add a download route that serves a file.

## Exercises
- Run locally on a non-default port.
- Bind to `127.0.0.1` vs `0.0.0.0` and note differences.