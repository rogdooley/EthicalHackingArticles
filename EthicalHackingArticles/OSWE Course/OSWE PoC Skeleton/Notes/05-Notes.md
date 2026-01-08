# 05 – Structured Logging for Exploit Development

## Why Logging Matters in Exploit Code

Explain that once control flow becomes non-linear (retries, branching, stages),
visibility becomes the limiting factor.
Print statements stop scaling as soon as something fails unexpectedly.

Key idea:
Logging is not about verbosity — it’s about **knowing what happened and why**.

---

## Logging vs Print Statements

Contrast:
- `print()` as a transient debugging aid
- logging as a persistent execution record

Highlight common problems with print-based PoCs:
- No timestamps
- No severity distinction
- No persistence
- No way to reconstruct a failed run

Make it clear this is **not** about enterprise logging practices.

---

## What We Actually Need from Logging in a PoC

Define exploit-focused logging requirements:

- Clear success / failure indicators
- Stage-aware messages
- Optional persistence to disk
- Minimal setup cost
- No external dependencies
- Works under exam pressure

This section grounds the design before showing any code.

---

## Logging as an Audit Trail, Not Just Debug Output

Introduce the idea that logs serve two purposes:
- **During execution**: understand what the exploit is doing now
- **After execution**: understand what the exploit already did

Tie this back to Article 04:
Stages + logging = traceable exploit progression.

---

## Severity Levels in an Exploit Context

Explain why traditional levels still map cleanly:

- INFO → normal progress
- SUCCESS → state transitions
- WARNING → recoverable failures
- ERROR → stage failure
- DEBUG → exploratory output

Emphasize semantic meaning over strict correctness.

---

## Timers, Durations, and Feedback Loops

Introduce timing as a logging concern:
- Measuring stage duration
- Identifying slow or unstable steps
- Giving feedback during long-running exploits

Keep this conceptual — no performance benchmarking.

---

## Console Output vs File Logging

Discuss the split:
- Console output for operator awareness
- File logs for auditing and replay

Make the point that **file logging is optional but powerful**,
especially when retries and persistence are involved.

---

## Where OffsecLogger Fits

Position your logger clearly:
- A thin, opinionated wrapper
- Designed for exploit ergonomics, not extensibility
- Optimized for human reading under pressure

Avoid comparisons to enterprise logging frameworks.

---

## What This Logger Does *Not* Try to Solve

Important boundary-setting section:
- No async logging
- No log rotation
- No structured JSON logs (yet)
- No external log aggregation

This prevents reader expectation drift.

---

## Integrating Logging with Stages

Explain (without code-heavy examples):
- One logger instance per run
- Logs tied to stages, not functions
- Logging state transitions explicitly

This reinforces the mental model from Article 04.

---

## Common Logging Anti-Patterns in PoCs

Briefly call out mistakes:
- Logging everything
- Logging nothing
- Logging only failures
- Mixing debugging and reporting output

This helps readers self-correct.

---

## Where to Stop Logging (and Why)

Explain that:
- Logging should taper off once terminal state is reached
- Final logs should summarize, not spam
- The goal is confidence, not exhaustiveness

This is a natural wind-down.

---

## Transition to the Next Article

End with a forward-looking but restrained transition, e.g.:

Now that we can *see* what our exploit is doing and *why* it made certain decisions,
the next step is organizing exploit code for reuse and long-term maintainability.
In the next article, we’ll look at how to factor PoCs into reusable components
without losing clarity or speed.

(Adjust depending on Article 06’s topic.)