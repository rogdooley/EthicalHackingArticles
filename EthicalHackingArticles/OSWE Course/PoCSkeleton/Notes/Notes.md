Here’s a clean, import-ready Markdown file summarizing **Article 1: Philosophy & Repo Layout** — structured for Obsidian or your internal knowledge base. It preserves hierarchy and reasoning but omits fluff.

---

```
# Building a Professional PoC Skeleton for OSWE
## Article 1 – Philosophy & Repository Layout

### Overview
A reusable PoC skeleton makes your exploit scripts reproducible, auditable, and exam-ready.  
Goal: produce a **sync-first**, minimal-dependency structure that supports later async upgrades.

---

## 1. Why a Skeleton Matters
- **Reproducibility:** consistent CLI, explicit timeouts, controlled evidence directories.
- **Auditability:** structured logging and predictable output paths.
- **Maintainability:** typed dataclasses and small interfaces.
- **Exam Safety:** minimal dependencies, deterministic behavior.

---

## 2. OSWE Constraints
- Use only standard lib + `httpx`.
- No prompts unless `--interactive`.
- Always respect `--evidence-dir`.
- Deterministic names: `EXAM-YYYY/MM/DD`.
- Default safe operations; explicit `--cleanup` for destructive tasks.

---

## 3. Recommended Repository Layout
```

poc-skeleton/

├── README.md

├── pyproject.toml  /  requirements.txt

├── docs/

│   └─ article-1.md

├── scripts/

│   └─ poc_example.py

├── libs/

│   ├─ exploit_context.py

│   ├─ offsec_logger.py

│   ├─ http_client.py

│   └─ utils.py

├── examples/

│   └─ blind_sqli_sample/

│       ├─ server.py

│       └─ README.md

├── tests/

│   └─ test_context.py

└── outputs/          # created at runtime, .gitignore’d

```
---

## 4. Minimal README Template
```

# **PoC Skeleton (Sync-First)**

  

Requirements: Python 3.12+

python -m venv .venv

.venv/bin/pip install -r requirements.txt

  

Run:

python scripts/poc_example.py –target https://10.0.2.15 –evidence-dir outputs/exam01 –verbose

  

Policy:

- Evidence → --evidence-dir
    
- No interactive prompts unless --interactive
    
- Default timeout 10 s (override --timeout)
    
- Uses httpx for HTTP requests
    

````
---

## 5. Core Snippets

### CLI → ExploitContext
```python
from argparse import ArgumentParser
from libs.exploit_context import ExploitContext

def build_cli() -> ArgumentParser:
    p = ArgumentParser(description="OSWE PoC Skeleton (Sync-First)")
    p.add_argument("--target", required=True)
    p.add_argument("--evidence-dir", default="outputs/default")
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--verbose", action="store_true")
    return p

def main() -> None:
    args = build_cli().parse_args()
    ctx = ExploitContext(
        target=args.target,
        evidence_dir=args.evidence_dir,
        timeout=args.timeout
    )
````

### **Typed ExploitContext**

```
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ExploitContext:
    target: str
    evidence_dir: str
    timeout: int = 10
    proxy: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
```

### **Minimal OffsecLogger**

```
import logging
from typing import Any, Dict

class OffsecLogger:
    def __init__(self, ctx):
        self._log = logging.getLogger("offsec")

    def info(self, msg: str, **ctx: Dict[str, Any]) -> None:
        self._log.info(msg, extra=ctx)

    def evidence(self, name: str, payload: str) -> None:
        # write to evidence file
        pass
```

### **Evidence Writer**

```
from pathlib import Path

def write_evidence(evidence_dir: str, name: str, content: bytes) -> Path:
    p = Path(evidence_dir)
    p.mkdir(parents=True, exist_ok=True)
    out = p / name
    out.write_bytes(content)
    return out
```

---

## **6. Sync-First Rationale**

- Easier for new developers to reason about flow.
    
- Fewer pitfalls with shared mutable state.
    
- Async layer can later wrap identical interfaces (AsyncHttpClient).
    

---

## **7. Suggested PoC Phases**

1. **Validate:** confirm target availability.
    
2. **Recon:** enumerate endpoints.
    
3. **Exploit:** perform vulnerability action.
    
4. **Verify:** confirm success & collect proof.
    
5. **Cleanup:** close sessions & write proof.txt.
    

  

Each phase accepts (ctx, logger) and raises typed exceptions on failure.

---

## **8. Testing Strategy**

- Unit-test only non-exploit components:
    
    - Arg parser
        
    - Context validation
        
    - Evidence writer
        
    
- Use the in-memory DB (examples/blind_sqli_sample/server.py) for functional testing.
    

---

## **9. Weekly Authoring Plan**

|**Week**|**Focus**|**Output**|
|---|---|---|
|1|Article 1 (draft & repo layout)|Publish single article + README|
|2|Article 2 (CLI) + 3 (Context outline)|Batch publish|
|3|Full Article 3 + tests|Next batch|
|4 +|Articles 4–6 (Logging, Networking, Control flow)|Iterate|

---

## **10. Publishing Checklist**

- outputs/ ignored in VCS
    
- README references --evidence-dir
    
- Default timeout 10 s
    
- One minimal unit test
    
- Example proof.txt in outputs/
    

---

## **11. Future Articles (Planned)**

1. CLI Design and Argparse Patterns
    
2. ExploitContext and Configuration Handling
    
3. Structured Logging (OffsecLogger)
    
4. HTTP Client Abstraction (Sync → Async migration)
    
5. Control Flow and Stage Management
    
6. Concurrency Concepts (async vs threads)
    
7. Reporting & Evidence Automation
    
8. Testing & Linting for Exam Safety
    
9. Blind SQLi Example with Binary vs Linear Search
    

---

## **12. Notes for Future You**

- Blind SQLi will later use an in-memory SQLite DB served via Flask or http.server.
    
- Type hints and dataclasses are mandatory in all future articles.
    
- Evidence directory is always relative to repo root for reproducibility.
    

```
---

Would you like me to append a short **grader_checklist.md** (one page, concise table of artifacts and expected locations) so it’s bundled with this note set?
```