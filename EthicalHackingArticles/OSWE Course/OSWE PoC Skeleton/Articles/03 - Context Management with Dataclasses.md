---
title: 03 - Context Management with Dataclasses
series: OSWE PoC Skeleton
series_order: 3
tags:
  - oswe
  - web-300
  - exploit-development
  - poc
  - python
  - offensive-security
description: Centralizing exploit configuration and runtime state using Python dataclasses to simplify reuse, readability, and multi-stage PoC development.
---

In the [last article](<02 -  Argument Parsing for OSWE PoCs - argparse vs dotenv.md>), I described how using Python's argparse functionality allowed easy configuration of different command line arguments. OSWE Challenge Labs usually have a debug and a victim machine. Each VM has a different IP address on their network. While testing the exploit chain, depending on the student, one might move between the debug and victim vm...or not. _argparse_ easily allows the setting of each machines unique configuration without having to edit the PoC code. Parameters can be passed from the command line and stored internally. For example, the target could have input arguments like:

```python
parser.add_argument("--target-ip", type=str, required=True, help="Input file path")
    parser.add_argument("--target-port", type=int, default=80, help="Input file path")
```

After the arguments are read in, the arguments could be initialized in the following manner:

```python
args = parse_args()

target_ip = args.target_ip
target_port = args.target_port
```

As the number of required arguments grows, extracting and passing individual values quickly becomes repetitive and error-prone. Once I considered how many inputs the exploit required, I needed a way to pass this data cleanly between functions.

Before I explain what I eventually ended up doing to consolidate the collection of arguments, I'd like to briefly describe a method for organizing them. Given the course and lab objectives, some argument options seemed fairly transparent and connected (eg target vs attacker). As I was refining the structure throughout the labs, I learned that one can group arguments with argparse.  Grouping the arguments is really only for cosmetic purposes. Running the code with the `--help` option, when the arguments are grouped, will display the groupings together (see below).

I decided to group arguments using target, attacker, exploit, identity, and optional options.  To group options together, decide on a variable name for the grouping and then use `.add_argument_group("descripton")`. A basic groupings might look like:

```python
def parse_args():
    parser = argparse.ArgumentParser(description="OSWE Application Exploit.")

    # --- Target options ---
    target_group = parser.add_argument_group("Target options")
    target_group.add_argument(
        "--target-ip", type=str, required=True, help="Target server IP address"
    )
    target_group.add_argument(
        "--target-port",
        type=int,
        default=80,
        help="Target web frontend port (default: 80)",
    )
```

When using `--help` to find the options, grouped options are shown together. 

```bash
❯ uv run poc.py --help
usage: poc.py [-h] --target-ip TARGET_IP [--target-port TARGET_PORT] [--target-api-port TARGET_API_PORT] [--listening-ip LISTENING_IP]
               [--listening-port LISTENING_PORT] [--payload-port PAYLOAD_PORT] [--delay DELAY] [--user-file USER_FILE]
               [--save-identity SAVE_IDENTITY] [--register] [--complexity {low,medium,high}] [--include-address] [--include-phone]
               [--charset {alpha,alnum,hex,ascii,symbols,base64,numeric}] [--proxy PROXY]

OSWE Application Exploit.

options:
  -h, --help            show this help message and exit

Target options:
  --target-ip TARGET_IP
                        Target server IP address
  --target-port TARGET_PORT
                        Target web frontend port (default: 80)
  --target-api-port TARGET_API_PORT
                        Target API port (default: 5000)

Attacker options:
  --listening-ip LISTENING_IP
                        IP to listen on for reverse shell (default: 127.0.0.1)
  --listening-port LISTENING_PORT
                        Port to listen for reverse shell (default: 9001)
  --payload-port PAYLOAD_PORT
                        Port to listen for xss or other payload (default: 9999)

Exploit options:
  --delay DELAY         Response delay in seconds for timing inference (default: 3)

Identity options:
  --user-file USER_FILE
                        Path to existing exploit user JSON (default: user.json)
  --save-identity SAVE_IDENTITY
                        Path to save newly generated identity JSON
  --register            Whether the user has already been registered
  --complexity {low,medium,high}
                        Password complexity
  --include-address     Include street address
  --include-phone       Include phone number

Optional options:
  --charset {alpha,alnum,hex,ascii,symbols,base64,numeric}
                        Charset to use for blind SQLi password extraction.
  --proxy PROXY         Turn on Burp Suite proxy for debugging.
 
```

The grouping itself does not change behavior, but it significantly improves readability once the number of options grows.

Before introducing a context object, most exploit scripts grow organically: variables are defined near main(), then slowly threaded through multiple function calls. As the exploit evolves, function signatures grow longer, ordering becomes brittle, and small changes require touching many call sites.

```text
Before:
    create_account(target_ip, target_port, user, proxy, timeout)
    sign_in(target_ip, target_port, user, proxy)
    extract_flag(target_ip, target_port, session)

After:
    create_account(ctx, user)
    sign_in(ctx, user)
    extract_flag(ctx)
```

Dataclasses come with `__init__` baked-in and the data structure can be printed as a dictionary without having to add a `__repr__` method. We can use the `@dataclass` decorator to initialize the class. Notice the use of `slots=True` on the dataclass. This enforces a fixed schema, preventing accidental attribute creation due to typos and making the structure of the context explicit. While slots can provide performance benefits in some scenarios, its primary purpose here is correctness and discipline rather than speed.

I named the class `ExploitContext`, but this was just a personal choice. What we are building with `ExploitContext` is a structured object which will contain the state required to execute most of the exploit. I say most here, because I ended up having a different structure for simulating and registering user accounts. By having a singular structure, important data can be passed through layers of functions without having to have a multitude of function arguments and when layering function calls, the passing of said information is simplified.

ExploitContext is intentionally **not** a replacement for HTTP sessions, request state, or per-request variables. Transport concerns (cookies, headers, retries) live in requests or httpx sessions. The context exists to describe the environment the exploit operates in, not every transient detail of execution.

At a high level, `ExploitContext` is intended to hold:

- Target-specific configuration (IP addresses, ports, protocol)
- Attacker-side configuration (listener and payload delivery ports)
- Stable runtime identifiers and configuration needed across exploit steps
- Metadata useful for auditing or reporting (PoC ID, vulnerability name)

Below is an example of how to start constructing the class and initializing it. 

```python
# additional imports go here
from dataclasses import dataclass

# any global variables, etc... go here

@dataclass(slots=True)
class ExploitContext:
    target_ip: str
    target_port: int
    target_api_port: int
    attacker_ip: str
    attacker_port: int
    payload_port: int
    protocol: str = "http"
    
# more code
# def main()
# more code

    ctx = ExploitContext(
        target_ip=args.target_ip,
        target_port=args.target_port,
        attacker_ip=args.listening_ip,
        attacker_port=args.listening_port,
        protocol="http"
    )    
    
# more code
```

- `target_port`: victim's web front end
- `target_api_port`: victim's API service (when present)
- `attacker_port`: interactive callbacks (e.g., reverse shell)
- `payload_port`: hosted payload delivery

Once the context exists, exploit functions can accept a single argument (`ctx`), instead of a long list of parameters. This makes function signatures stable even as the exploit grows and allows new fields to be added to the context without additional rewriting.

At this point, we have a single object that represents everything the exploit needs to know about its environment and current state. Configuration, runtime values, and metadata are no longer scattered across the codebase.

Rather than passing configuration values through every function, the context moves unchanged through the exploit, accumulating state as needed.

```text
┌───────────────┐
│ CLI / argparse│
└───────┬───────┘
        │
        │ parse_args()
        ▼
┌────────────────────┐
│  ExploitContext    │
│  (ctx)             │
│────────────────────│
│ target_ip          │
│ target_port        │
│ attacker_ip        │
│ payload_port       │
│ protocol           │
│ metadata / state   │
└─────────┬──────────┘
          │
          │ passed as a single argument
          ▼
┌────────────────────┐
│ create_account(ctx)│
└────────────────────┘
          │
          ▼
┌────────────────────┐
│ sign_in(ctx)       │
└────────────────────┘
          │
          ▼
┌────────────────────┐
│ exploit_step(ctx)  │
└────────────────────┘
```

What we *do not* yet have is a clear model for how exploit stages relate to one another. In practice, most PoCs grow into long `main()` functions with deeply intertwined control flow, retries, and conditional logic. In the next article, we’ll address that problem directly by introducing explicit stage and control-flow management, using the context as the shared state between stages.

This article focuses on _what the context is_, not _everything it can do_. Helpers for URL construction, logging, and orchestration are intentionally deferred to later articles.
#### An example of how `ExploitContext` evolves

```python
# imports and code
from dataclasses import dataclass, field

# more imports anc code possible here

@dataclass(slots=True)
class ExploitContext:
    target_ip: str
    target_port: int
    target_api_port: int
    attacker_ip: str
    attacker_port: int
    payload_port: int
    protocol: str = "http"

    # Runtime-only fields
    output_path: Path = field(
        default_factory=lambda: Path("exploit_context.json"), repr=False
    )

    # --- Factory constructor from argparse -

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ExploitContext":
        """Build an ExploitContext from CLI arguments."""
        return cls(
            target_ip=args.target_ip,
            target_port=args.target_port,  # maps to --target-port
            target_api_port=args.target_api_port,  # maps to --target-api-port
            attacker_ip=args.listening_ip,  # maps to --listening-ip
            attacker_port=args.listening_port,  # maps to --listening-port
            payload_port=args.payload_port # maps to --payload-port
        )

# Code for the PoC

def main():
    args = parse_args()
    
    # more initialization code might be here
    
    ctx = ExploitContext.from_args(args)

```

What I’ve done here is make the construction of `ExploitContext `simpler by reducing the amount of boilerplate code required during initialization. Instead of deconstructing parsed arguments inside `main()`, the from_args(args) classmethod accepts the full `argparse.Namespace` and is responsible for mapping CLI options directly into the context. Placing this mapping logic inside `ExploitContext` keeps construction concerns close to the data they produce, reduces duplication, and makes future refactors safer when CLI options change.

Because from_args is defined as a `@classmethod`, it receives the class itself (`cls`) rather than an instance, allowing it to act as an alternate constructor. The `argparse.Namespace` passed into `from_args` contains all parsed command-line options, which are selectively extracted and used to build the context in a single, centralized place. Finally, `output_path` is initialized at runtime to define where the context may be serialized. This file can be used for auditing, debugging, or state restoration if desired, but its use is optional and left entirely to the programmer.

This structure is not a template you must copy verbatim. The goal is to demonstrate a pattern that scales as exploits grow, not to prescribe a fixed schema.

In the next article, we’ll focus on structuring exploit execution itself by introducing explicit stages and control flow that operate over the shared context so the PoC is well-organized and maintainable.