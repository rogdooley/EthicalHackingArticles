## ExploitContext Summary

- **Purpose**: Centralizes configuration, identity, session, and metadata for a single PoC run. Reduces argument passing and makes stage chaining easier.

### Structure
- `@dataclass(slots=True)`: Uses Python 3.10+ slots for performance and memory efficiency.

### Core Fields
- `target_ip`, `web_port`, `api_port`: Target system parameters
- `attacker_ip`, `attacker_port`, `payload_port`: Attacker-side listener/payload ports
- `protocol`: Defaults to `"http"`; used in URL generation

### Auth Fields
- `token`: JWT or API token used in requests
- `token_name`: Name of the token header/cookie (e.g., `"X-Auth-Token"`)
- `session_cookie`: Session identifier from the target webapp

### Metadata
- `vuln_name`: Label for the vulnerability being exploited (e.g., `"SQLi-Token-Bypass"`)
- `poc_id`: Unique identifier for the PoC run or exploit (e.g., `"lab1-chain01"`)
- `notes`: Freeform notes, unused at runtime

### Runtime-Only
- `output_path`: Where to save/load the context (`exploit_context.json` by default); excluded from serialization

### Methods
- `from_args(args)`: Class method to instantiate from `argparse.Namespace`
- `web_url()`, `api_url()`, `attacker_url()`: Construct base URLs with correct protocol and optional port omission
- `save()`: Write context to JSON, excluding runtime-only fields
- `from_file(path)`: Load a context file; ignores unknown fields and normalizes port types

### Notes
- Designed for chaining exploit stages cleanly
- Can be extended with `.identity`, `.headers`, `.stage`, etc. later
- Explicitly avoids globals; meant to be passed to all stage functions

## Design Choices in `ExploitContext`

### [ ] `@dataclass(slots=True)`
- **Why?**  
  - `slots=True` reduces memory overhead and attribute lookup time.
  - Prevents accidental addition of new attributes (immutable structure).
  - Ideal for a config/state object that should not mutate unexpectedly.
- **Python version note**: Requires 3.10+.

---

### [ ] `field(..., repr=False)` for `output_path`
- **Why?**
  - Marks `output_path` as a runtime-only field not meant to be part of JSON serialization or printed `repr()`.
  - Keeps logs/debug output focused on meaningful exploit parameters, not file paths.
  - Still allows you to change the output path programmatically.

---

### [ ] `.from_args()` Class Method
- **Why?**
  - Cleanly maps `argparse.Namespace` into a structured config object.
  - Explicit field mapping makes CLI→context translation easy to audit.
  - Prevents context construction logic from being spread across the codebase.

---

### [ ] `.save()` and `.from_file()`
- **Why?**
  - Enables persistence between exploit stages or across sessions.
  - Useful for staged PoCs (e.g., registration → login → exploit), where you want to resume or replay with prior state.
  - Supports audit and reproducibility—critical in OSWE reporting.

---

### [ ] `web_url()`, `api_url()`, `attacker_url()` helpers
- **Why?**
  - Prevents redundant URL formatting logic across scripts.
  - Auto-handles port stripping (`:80` for HTTP, `:443` for HTTPS) for cleaner output/logs.
  - Keeps PoC logic readable (`httpx.get(ctx.api_url() + "/auth")` is cleaner than rebuilding every time).

---

### [ ] `CHARSETS`, `token`, `vuln_name`, etc.
- **Why?**
  - Adds context-awareness for the specific vulnerability being exploited.
  - Allows `ctx.notes`, `ctx.poc_id`, `ctx.charset` to be referenced in reports/logs without hardcoding.
  - Enables more advanced behavior later: dynamic stage labeling, exploit metadata, conditional payload generation.

---

### [ ] Design Philosophy
- **Encapsulation**: All PoC-relevant state lives in one object, passed to all exploit stages.
- **Reusability**: Fields are generic enough to fit multiple exploit chains.
- **Extendability**: Easy to add `.identity`, `.headers`, `.request_log`, etc. later without rewriting everything.
- **Safe Defaults**: Defaults like `"http"` or port `80` make quick testing possible without excessive config.

---

## Optional Future Enhancements
- Add a `.from_env()` loader to parallel `.from_args()`
- Add `.as_headers()`, `.as_curl()` for payload/debug generation
- Include a `.stage` or `.step` tracker for multi-part exploits


## Appendix A – `ExploitContext` Design Reference

### A.1 Overview
`ExploitContext` is a centralized data structure used to track configuration, session state, metadata, and runtime artifacts during exploit development. It simplifies argument passing, reduces duplication, and supports chaining multi-stage attacks in OSWE-style PoCs.

---

### A.2 Core Fields

| Field Name       | Type         | Purpose                                      |
|------------------|--------------|----------------------------------------------|
| `target_ip`      | `str`        | Victim IP address                            |
| `web_port`       | `int`        | Frontend port for web access                 |
| `api_port`       | `int`        | Optional backend/API port                    |
| `attacker_ip`    | `str`        | Attacker host for callback or hosting files  |
| `attacker_port`  | `int`        | Port for reverse shells or listening         |
| `payload_port`   | `int`        | Port used for payload delivery (e.g., XSS)   |
| `protocol`       | `str`        | `http` or `https` (default: `http`)          |

---

### A.3 Auth & Metadata Fields

| Field Name       | Type           | Purpose                                      |
|------------------|----------------|----------------------------------------------|
| `token`          | `Optional[str]`| Auth token (e.g., JWT)                       |
| `token_name`     | `Optional[str]`| Header or cookie name for token              |
| `session_cookie` | `Optional[str]`| HTTP session ID                              |
| `vuln_name`      | `Optional[str]`| Label for exploited vulnerability            |
| `poc_id`         | `Optional[str]`| Unique ID for this exploit run               |
| `notes`          | `str`          | Arbitrary comments or context notes          |

---

### A.4 Runtime & Persistence

| Field Name       | Type           | Purpose                                      |
|------------------|----------------|----------------------------------------------|
| `output_path`    | `Path`         | File location to save/load context state     |

- Excluded from serialization (`repr=False`)
- Used by `.save()` and `.from_file()` for PoC persistence

---

### A.5 Constructor Methods

- `from_args(args: argparse.Namespace)`  
  Constructs the context from CLI arguments

- `from_file(path: Path)`  
  Loads a previously saved context (with type recovery)

---

### A.6 Utility Methods

| Method           | Description                                     |
|------------------|-------------------------------------------------|
| `web_url()`      | Returns full base URL to target web interface   |
| `api_url()`      | Returns full base URL to target API             |
| `attacker_url()` | Returns full base URL to local listener         |
| `_make_url()`    | Internal utility for formatting URLs cleanly    |
| `save()`         | Serializes context to JSON file (excluding `output_path`) |

---

### A.7 Design Rationale

- Uses `@dataclass(slots=True)` for performance and safety
- Consolidates all exploit-related variables into a single object
- Avoids use of global variables
- Portable across multiple labs and easily extensible

---

### A.8 Suggested Extensions

- `.from_env()` or `.from_config()` to support dotenv-based workflows
- `.as_headers()` or `.inject_auth()` for reusable request prep
- `.stage` or `.step` tracker for multi-stage exploit flows

::: info ExploitContext Reference

Use `ExploitContext` to manage:

- **Target Details**  
  `ctx.target_ip`, `ctx.web_port`, `ctx.api_url()`

- **Attacker Config**  
  `ctx.attacker_ip`, `ctx.payload_port`, `ctx.attacker_url()`

- **Tokens & Auth**  
  `ctx.token`, `ctx.session_cookie`, `ctx.token_name`

- **Metadata**  
  `ctx.vuln_name`, `ctx.poc_id`, `ctx.notes`

- **Persistence**  
  Save: `ctx.save()`  
  Load: `ExploitContext.from_file(...)`

Default file: `exploit_context.json`
:::