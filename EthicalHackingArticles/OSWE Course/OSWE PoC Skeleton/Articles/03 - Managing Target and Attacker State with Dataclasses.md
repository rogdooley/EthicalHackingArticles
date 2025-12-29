## Drafting Checklist – Article 3: Context Management

- [ ] Introduce the need for a central object or structure to hold configuration, session state, and metadata
- [ ] Define what kinds of data this structure should track: base URL, headers, cookies, tokens, session, user info, etc.
- [ ] Mention that this helps avoid passing dozens of function arguments around
- [ ] Justify using a `@dataclass` (mention `slots=True` and Python 3.12+ support)
- [ ] Explain how `ExploitContext` can be populated from `argparse` or `.env` values (parsed config already exists)
- [ ] Include reasoning for separating user identity fields vs target-specific fields vs exploit state
- [ ] Consider including a `.from_config(config: dict)` constructor or similar
- [ ] Add commentary on why this structure is critical for reuse between labs and exploit stages


From the last article, I described how using Python's argparse functionality allowed the easy use of configuring different command line arguments along with default behavior so that when executing a PoC script, when various values like the target IP address change, reflecting that change is straightforward without needed to touch the written script. With those parameters now available internally, one way to store the values internally involve initializing variables to store the values. For example, the target could have input arguments like:

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

Based on what I have outlined, the argument initializing list could end up very long. 

Before I explain what I eventually ended up doing to consolidate all the arguments I chose to have, I'd like to briefly run through some of them and a method of organizing them. Based on the objectives for each lab, some options seemed fairly transparent. As I was refining the structure throughout the labs, I learned that one can group arguments with argparse. My choice of grouping was target, attacker, exploit, identity, and optional options.  To group options together, decide on a variable name for the grouping and then use `.add_argument_group("descripton")`. An example of how to start building groupings might look like:

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

When using `--help` to find the options, you can see how similar options are grouped. Maybe you wouldn't group them like this. I did find this fairly helpful. 

```bash
❯ uv run main.py --help
usage: main.py [-h] --target-ip TARGET_IP [--target-port TARGET_PORT] [--target-api-port TARGET_API_PORT] [--listening-ip LISTENING_IP]
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

I was at 15 options which I could set, but honestly, that is a lot variables to import and keep track of. Notice all these options can be thought of as data. Some of these we'd obviously combine to make a url or to setup a listener or start a web server to deliver a payload. The data nature lended itself to Python's dataclass. There are some instant gains for tying these values to a dataclass. Dataclasses come with `__init__` baked-in and the data structure can be printed as a dictionary without having to concoct a string method for the class. Since we're writing exploits, I chose to call the class `ExploitContext`. I started with a simple construct for the class:

```python
@dataclass(slots=True)
class ExploitContext:
    target_ip: str
    web_port: int
    api_port: int
    attacker_ip: str
    attacker_port: int
    payload_port: int
    protocol: str = "http"

    # Auth state
    token: Optional[str] = None
    token_name: Optional[str] = None
    session_cookie: Optional[str] = None

    # Metadata
    vuln_name: Optional[str] = None
    poc_id: Optional[str] = None
    notes: str = ""

    # Runtime-only fields
    output_path: Path = field(
        default_factory=lambda: Path("exploit_context.json"), repr=False
    )
```

```python
    ctx = ExploitContext(
        target_ip=args.target_ip,
        target_port=args.target_port,
        attacker_ip=args.listening_ip,
        attacker_port=args.listening_port,
        protocol="http",
        vuln_name="authrise",
        poc_id="01",
    )
```