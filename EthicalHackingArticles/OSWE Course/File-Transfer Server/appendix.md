---
title: "Appendix – Testing, Troubleshooting, and Hardening"
description: "Checklists for functional testing, common failures, and security-minded tweaks."
tags: [testing, troubleshooting, hardening]
---

# Appendix – Testing, Troubleshooting, and Hardening

## Functional Test Checklist
- Port binding, route reachability, file presence, success + error paths.
- Limit enforcement, callback firing, clean shutdown.

## Common Issues
- Port in use; wrong working directory; missing permissions; malformed base64; incorrect `Content-Type`.

## Hardening Ideas (Optional)
- Randomized route length and charset.
- Loopback-only admin endpoints and optional bind control.
- Max payload size, simple token/HMAC on admin endpoints (if needed).
- Minimal request logging (avoid over-collection).

## Operational Hygiene
- Artifact directory hygiene and naming convention.
- Log retention/rotation for lab notes.