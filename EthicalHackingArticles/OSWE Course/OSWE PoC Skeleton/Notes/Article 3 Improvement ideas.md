## Editorial Update – Locking the ExploitContext Design

The current implementation of `ExploitContext` represents a stable and well-scoped baseline. At this point, the article should shift from *exploration* to *justification*. The goal is no longer to enumerate what could be added, but to explain why the current boundaries exist.

The notes below supersede earlier “possible additions” guidance.

---

## 1. ExploitContext Scope Is Correct — Do Not Absorb Identity Logic

The current construction pattern deliberately keeps identity generation outside of `ExploitContext`. This is a good design decision and should be defended explicitly in the article.

Key points to state clearly:
- `ExploitContext` owns **environment and exploit state**
- Identity generation is a **supporting subsystem**
- Identity inputs (`extras`, `overrides`) are *derived* from CLI arguments, not core exploit state
- Mixing identity internals into context would tightly couple unrelated concerns

This separation keeps the context reusable even for exploits that do not require user creation.

---

## 2. Factory Construction via `from_args` Is the Right Abstraction Boundary

The `from_args()` classmethod cleanly isolates:
- CLI parsing concerns
- Naming mismatches between flags and fields
- Context initialization logic

Editorial emphasis:
- Argument parsing should not leak into exploit logic
- Exploit code should depend on `ExploitContext`, not `argparse.Namespace`
- Future config sources (dotenv, JSON, test harnesses) can add parallel constructors

You do **not** need to add `.from_config()` now. Mention it as a future option only.

---

## 3. URL Helpers Are a Major Design Win — Call This Out Explicitly

The `_make_url()` + `web_url()` / `api_url()` helpers are exactly the kind of logic that belongs in context.

Suggested framing:
- URL construction is easy to get subtly wrong
- Centralizing it prevents inconsistencies across exploit stages
- Default-port elision avoids noisy URLs in logs and output
- Protocol handling becomes declarative instead of ad-hoc

This is one of the strongest parts of the design and worth highlighting.

---

## 4. Persistence Is Sufficient — Avoid Turning This Into a State Machine

The current persistence model is intentionally simple:
- Explicit save
- JSON format
- Redaction via exclusion (`output_path`)
- Type recovery on load

Editorial guidance:
- This is for debugging, replay, and audit trails
- Not intended as a resumable exploit engine (yet)
- Runtime-only state (live sessions, sockets) is excluded by design

Do **not** add resumability, checkpoints, or live object restoration at this stage.

---

## 5. Field Naming: Explain the Trade-Off Once, Then Move On

You’ve chosen:
- `web_port` vs `api_port`
- `attacker_port` vs `payload_port`

This is reasonable, but readers may wonder why `target_port` was renamed.

Add one short explanation:
- Ports are named by *role*, not by CLI flag
- CLI flags optimize ergonomics
- Context fields optimize clarity during exploit execution

One paragraph is enough. Do not dwell on it.

---

## 6. Runtime vs Configuration Is Now Clear Enough

You already have:
- Configuration fields
- Auth state
- Metadata
- Runtime-only fields

