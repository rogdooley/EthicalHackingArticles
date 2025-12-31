# Article 3 – Context Management
## Editorial Notes and Improvement Targets

This document captures suggested improvements and expansion points for Article 3. The goal is to make the `ExploitContext` comprehensive, reusable, and exploit-focused without turning the article into a Python or dataclasses tutorial.

---

## 1. Clarify the Core Problem Earlier

The article currently shows *how* arguments are grouped and *why* that helps, but it should more explicitly state the **problem** being solved before introducing `ExploitContext`.

Suggested framing to reinforce:
- The problem is not argparse
- The problem is *state sprawl*
- Too many loosely-related variables passed between functions
- Too many implicit dependencies between exploit stages

You may want one explicit sentence along the lines of:
> Once argument parsing stabilized, the larger problem became how to carry configuration, runtime state, and discovered data through the exploit without passing dozens of parameters between functions.

This primes the reader for why a context object is necessary.

---

## 2. Explicitly Categorize What the Context Holds

You already imply this with comments, but making it explicit will improve clarity.

Recommended categories to describe in prose:
- **Target configuration** (what you are attacking)
- **Attacker configuration** (how you are interacting)
- **Runtime/session state** (what changes as the exploit runs)
- **Metadata** (operator-facing or reporting information)

This helps readers understand that `ExploitContext` is not “just config”, but a living object that evolves as the exploit progresses.

---

## 3. Naming Consistency (Important)

Ensure field names align cleanly across:
- argparse arguments
- dataclass fields
- downstream usage

You’ve already corrected this partially. Maintain consistency like:
- `target_ip`, `target_port`, `target_api_port`
- `attacker_ip`, `attacker_port`, `payload_port`

Avoid mixing `web_port`, `api_port`, and `target_port` unless you explicitly justify the distinction.

This prevents subtle bugs and reduces cognitive overhead when reading exploit stages later.

---

## 4. Add Derived Properties (High Value, Low Complexity)

To make the context *useful*, not just *centralized*, consider adding derived properties:

Examples to mention (not necessarily implement fully yet):
- `target_base_url`
- `api_base_url`
- `attacker_base_url`
- `is_https`
- `proxies` mapping (for httpx)
- `default_headers`

Explain the benefit:
- Prevents recomputing URLs inconsistently
- Centralizes protocol/port logic
- Reduces duplicated string formatting across exploit stages

This keeps URL logic out of individual exploit functions.

---

## 5. Introduce a Construction Pattern

Right now, `ExploitContext` is instantiated manually from `args`.

Recommend introducing (or at least describing) one of:
- `@classmethod from_args(args)`
- `@classmethod from_config(config: dict)`

Editorial guidance:
- argparse or dotenv should produce a normalized config
- `ExploitContext` should be built from that config in one place
- This isolates input parsing from exploit logic

This also ties cleanly back to Article 2.

---

## 6. Validation Belongs in the Context

Consider adding a short section explaining that:
- Validation should live *with* the data
- Not scattered across exploit stages

Examples of checks worth mentioning:
- Required fields present
- Port ranges valid
- Protocol values sane
- Proxy format reasonable
- Payload port only required when payload hosting is used

You do not need to show all validation code—just justify why it belongs here.

---

## 7. Distinguish Immutable vs Runtime Fields

You already hint at this with “Runtime-only fields”.

Make the distinction explicit:
- Some fields should never change after initialization (target/attacker config)
- Others will evolve (tokens, cookies, stage markers)

This prepares readers for later articles on:
- Stage management
- Logging
- State transitions

---

## 8. Add Minimal Stage / Run Tracking

To support multi-stage exploits later, consider mentioning:
- `run_id` (unique per execution)
- `stage` or `stages_completed`

Explain why:
- Log correlation
- Debugging failed chains
- Re-running partial exploits

This connects directly to the upcoming logging article.

---

## 9. Discovered Data vs Operator Configuration

Strongly consider separating:
- Operator-provided configuration
- Data discovered during exploitation

A simple pattern to mention:
- `discovered: dict[str, Any]`

Examples of what belongs there:
- Leaked secrets
- CSRF tokens
- Admin endpoints
- Magic link tokens

This avoids ad-hoc globals and keeps exploit state explicit.

---

## 10. Serialization and Redaction (Mention, Don’t Overbuild)

You already include `output_path`. Good.

Suggested commentary to add:
- Contexts are often saved for debugging or reporting
- Not all fields should be serialized
- Sensitive fields should be redacted by default

This justifies:
- `repr=False`
- future `to_dict(redact=True)` methods

---

## 11. Keep the Dataclass Discussion Focused

Limit dataclass-specific explanation to:
- `slots=True` (memory, typo resistance)
- `default_factory` for mutable fields
- Why `frozen=False` is intentional

Avoid deep dives into:
- ordering
- comparisons
- advanced dataclass flags

This keeps the article exploit-focused, not language-focused.

---

## 12. Suggested Transition to the Next Article

To close Article 3 cleanly, tee up logging:

Suggested transition concept:
> Now that configuration and runtime state live in a single, structured object, we can log consistently without passing context manually. In the next article, we’ll build structured logging that automatically includes context metadata such as target, stage, and run ID.

This creates a natural bridge to the logging article.

---

## Summary

Article 3 is shaping up well. The remaining work is primarily:
- Making the motivation explicit
- Clarifying boundaries and categories
- Showing how the context enables later stages (logging, flow control)

Focus on **why the context exists**, not just **how it’s implemented**.