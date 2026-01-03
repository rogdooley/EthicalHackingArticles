# 04 - Control Flow and Stage Management

## Why control flow becomes the dominant problem

By the time I reached my later challenge labs, configuration was no longer the hard part.  
The PoCs worked, but the difficulty shifted to understanding *what happens next*, *why a retry occurs*, and *which pieces of state need to be reset when something fails*.

In my later PoCs (for example, `main(3).py`), the exploit logic is correct, but control flow is implicit rather than explicit. This article explains why that happens and how to reason about it.

---

## A realistic view of OSWE-style PoCs

OSWE PoCs rarely look like clean pipelines. They usually involve:

- Account creation or reuse
- Authentication and session handling
- Timing-based inference
- Conditional retries
- Privilege escalation
- Payload delivery

In practice, these steps *must* happen in a specific order. That order is the exploit.

---

## Implicit stages in a real PoC

Even without formal stage objects, my PoCs already have clear stages:

- User registration or loading
- Login and session establishment
- Oracle construction
- Data extraction
- Privileged access
- Post-exploitation (flags, shells, uploads)

These stages exist logically, even if they are not encoded as first-class concepts.

**This is intentional, not a mistake.**

---

## Why everything ends up in `main()`

In `main(3).py`, most orchestration happens in `main()` because:

- The exploit must proceed linearly
- Later steps depend on the success of earlier ones
- Recovery logic (re-login, retries, sleeps) depends on local context

Reducing `main()` to a single loop of function calls *would not remove complexity* — it would only move it elsewhere.

This is an important distinction.

---

## Separation of concerns vs separation of flow

In these PoCs:

- **Separation of concerns** is handled well  
  (helpers for extraction, login, oracles, uploads)

- **Separation of flow** is not explicit  
  (control logic is distributed across loops and conditionals)

This article focuses on *flow*, not refactoring helpers.

---

## Where control flow becomes hard to reason about

Using `main(3).py` as a reference, common friction points include:

- Retry loops embedded inside extraction logic
- Session invalidation forcing re-authentication
- Oracle lambdas rebuilt after failure
- Conditional exits that depend on timing behavior

None of these are wrong — but they make it hard to answer:

- “What stage am I in?”
- “Why did we restart this step?”
- “What state is safe to reuse?”

---

## What “stage management” actually means here

Stage management does **not** mean:

- A framework
- A scheduler
- A class hierarchy
- Abstract base classes

In this context, a *stage* is simply:

> A named unit of exploit intent that can succeed, fail, or require recovery.

Nothing more.

---

## Making stages explicit without rewriting the exploit

A useful mental model is:

```text
[ setup ] → [ authenticate ] → [ extract ] → [ escalate ] → [ post-exploit ]
```

In main(3).py, these already exist — they’re just implicit.

Stage management starts by naming these transitions, not restructuring the code.

⸻

Where flaws can be called out (constructively)

This is where you should be honest and helpful to beginners.

Examples you can safely point out:
	•	Retry logic is mixed with exploit logic
	•	Recovery paths are correct but not centralized
	•	Control flow decisions depend on side effects
	•	Success and failure conditions are implicit

Frame these as natural outcomes of exploit development, not mistakes.

⸻

Why this still worked (and why that matters)

Despite the complexity, the PoCs succeed because:
	•	The order of operations is correct
	•	State is carefully rebuilt when needed
	•	Failures are handled pragmatically
	•	Logic is explicit, even if verbose

This matters because it shows beginners that working code comes before elegant structure.

⸻

What explicit stage management would improve

Without changing exploit behavior, stage management would:
	•	Make execution order visible
	•	Localize retry decisions
	•	Clarify recovery paths
	•	Reduce cognitive load during debugging

This is about readability and reasoning, not performance.

⸻

What this article does not implement yet

Intentionally deferred:
	•	Logging integration
	•	Async orchestration
	•	Stage persistence
	•	Resume/replay mechanics

Those build on top of stage awareness.

⸻

Transition to the next article

At this point, the exploit has:
	•	Centralized configuration
	•	A shared context
	•	Implicit but well-defined stages

The remaining problem is visibility.

In the next article, we’ll focus on structured logging that aligns with exploit stages, making execution traceable without polluting exploit logic.

---

## Where to explicitly reference `main(3).py`

You should reference it in **three places only**:

1. When introducing implicit stages  
2. When explaining why `main()` stayed large  
3. When discussing retry and recovery complexity  

Do **not** annotate line-by-line. High-level references are enough.

---

## Editorial guidance on “flaws”

Use language like:

- “natural consequence”
- “pragmatic choice”
- “worked, but was hard to reason about”
- “good enough to pass the lab, but harder to maintain”

Avoid:

- “bug”
- “bad design”
- “wrong”
- “should have”

You are teaching **thinking**, not policing code.

---

## Final reassurance

You are **not underqualified** for this series.

What you’re documenting is exactly how exploit code evolves in real environments:
- correctness first
- clarity later
- structure last

That honesty is what will make Article 04 land.



📌 Callout: Why a Large main() Is Sometimes the Right Choice

In exploit development, a large main() function is not automatically a design failure.

Unlike typical application code, exploit PoCs often require:
	•	Strict execution order
	•	Conditional retries and backtracking
	•	Explicit recovery logic after partial failure
	•	Manual pacing (sleep, re-authentication, session resets)

These concerns are the exploit, not incidental complexity.

Pushing this logic into deeply nested helper functions can make the exploit harder to reason about, not easier. Keeping orchestration visible in main() allows the reader to understand:
	•	What stage the exploit is currently in
	•	Why a retry or reset occurred
	•	Which steps are safe to repeat and which are not

In practice, many successful OSWE PoCs prioritize explicit control flow over minimal function size. Refactoring should improve clarity — not hide the exploit’s logic behind abstraction.

A large main() is acceptable as long as:
	•	Each step has a clear purpose
	•	Control flow is readable
	•	Side effects are intentional and understood

Structure can always be refined later. Correctness and clarity come first

Here’s a tight mini-example you can include right after the callout.
It contrasts good large main() vs bad abstraction without shaming beginners.

⸻

Mini-Example: When a Large main() Helps — and When It Hurts

✔️ Large main() that improves clarity (good)

```python
def main():
    ctx = build_context()
    session = login(ctx)

    # Stage 1: establish baseline access
    if not verify_access(session):
        abort("Login failed")

    # Stage 2: extract admin token
    token = extract_token(ctx, session)
    if not token:
        session = relogin(ctx)
        token = extract_token(ctx, session)

    # Stage 3: escalate
    admin_session = login_as_admin(ctx, token)
    trigger_rce(ctx, admin_session)
```

Why this is OK:
	•	Execution order is explicit
	•	Retry logic is visible
	•	Each step maps directly to an exploit stage
	•	A reader can follow the attack path top-to-bottom

This is orchestration logic. Hiding it would reduce clarity.

⸻

❌ Over-abstracted version (worse for exploits)

```python
def main():
    ctx = build_context()
    run_exploit(ctx)

def run_exploit(ctx):
    session = prepare_session(ctx)
    escalate(ctx, session)

def escalate(ctx, session):
    token = get_token(ctx, session)
    admin = elevate(ctx, token)
    execute(ctx, admin)
```

What’s lost:
	•	Where retries happen
	•	Which steps are safe to repeat
	•	Why failures occur
	•	How stages relate to one another

The exploit flow is now scattered across functions with no visible state transitions.

⸻

Key takeaway for readers

In exploit PoCs, control flow is the exploit.
Abstract helpers should perform actions, not hide decisions.

Refactor only when it improves readability — not to satisfy stylistic rules from application development.

