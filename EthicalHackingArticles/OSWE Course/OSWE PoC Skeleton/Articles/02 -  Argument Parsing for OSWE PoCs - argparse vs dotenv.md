
Python's argparse module is the standard way to build command-line interfaces (CLI). For building a PoC exploit script, one can control  how inputs like targets, proxies, etc... are handled. By implementing a comprehensive design, the need to constantly re-write scripts between runs and between labs is eliminated. Generally, knowing all that might be built into the script is difficult. 

How many arguments do you need? Should there be defaults for certain arguments? What arguments will be required? Asking yourself questions like this will guide the shape of your script and the various arguments that are considered. What we're about to do isn't written in stone. Don't be afraid to remove items that don't make sense to your or to add ones that do. It's your skeleton to construct as you please. With that said, let's look at a basic command that we might build using argparse and dotenv.

As an alternative, some projects use an environment file to store configuration values. This approach can reduce command length and centralize configuration, which can be appealing when iterating quickly.

Below is an example `.env` file containing the same types of values we would otherwise pass via the command line. The goal here is not to build a full configuration system, but to highlight how this approach differs in practice.

```bash
uv add python-dotenv
```

```text
TARGET_IP=192.168.122.45
TARGET_PORT=8080
TARGET_API_PORT=5001

LISTENING_IP=10.8.0.5
LISTENING_PORT=9001
PAYLOAD_PORT=9999

DELAY=5
USER_FILE=user.json
SAVE_IDENTITY=output.json
REGISTER=true
COMPLEXITY=high
INCLUDE_ADDRESS=true
INCLUDE_PHONE=false
CHARSET=ascii
PROXY=http://127.0.0.1:8080
```

```python
from pathlib import Path

from dotenv import dotenv_values

CHARSETS = {
    "alpha": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "alnum": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "hex": "0123456789abcdef",
    "ascii": "".join(chr(i) for i in range(32, 127)),  # printable ASCII
    "symbols": "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~",
    "base64": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=",
    "numeric": "0123456789",
}

DEFAULTS = {
    "TARGET_PORT": 80,
    "TARGET_API_PORT": 5000,
    "LISTENING_IP": "127.0.0.1",
    "LISTENING_PORT": 9001,
    "PAYLOAD_PORT": 9999,
    "DELAY": 3,
    "USER_FILE": "user.json",
    "REGISTER": False,
    "INCLUDE_ADDRESS": False,
    "INCLUDE_PHONE": False,
    "CHARSET": "alnum",
    "PROXY": None,
}

REQUIRED_KEYS = ["TARGET_IP"]

INT_KEYS = {
    "TARGET_PORT",
    "TARGET_API_PORT",
    "LISTENING_PORT",
    "PAYLOAD_PORT",
    "DELAY",
}

BOOL_KEYS = {
    "REGISTER",
    "INCLUDE_ADDRESS",
    "INCLUDE_PHONE",
}


def parse_config(env_file: str = "authrise.env") -> dict[str, object]:
    env_path = Path(env_file)
    if not env_path.exists():
        raise FileNotFoundError(f"Missing environment file: {env_file}")

    env = dotenv_values(env_path)
    config = {**DEFAULTS, **env}  # env overrides defaults

    # Validate required
    for key in REQUIRED_KEYS:
        if key not in config or not config[key]:
            raise ValueError(f"Missing required config: {key}")

    # Convert types
    for key in INT_KEYS:
        if key in config:
            config[key] = int(config[key])

    for key in BOOL_KEYS:
        if key in config:
            val = str(config[key]).lower()
            config[key] = val in {"true", "1", "yes", "on"}

    return config


def main():
    config = parse_config()

    print(f"Register new user: {config['REGISTER']}")
    print(f"Target IP: {config['TARGET_IP']}")
    print(f"Target Port: {config['TARGET_PORT']}")
    print(f"Listening IP: {config['LISTENING_IP']}")
    print(f"Listening Port: {config['LISTENING_PORT']}")


if __name__ == "__main__":
    main()

```

```bash
❯ uv run poc-env.py
Register new user: True
Target IP: 192.168.122.45
Target Port: 8080
Listening IP: 10.8.0.5
Listening Port: 9001
```

One major difference between the dotenv and argparse methods is that when using argparse, you have an instant help flag that isn't available with the dotenv method. One can write a help method for a dotenv by adding in code like:

One immediate drawback of the environment file approach is discoverability. Unlike `argparse`, there is no built-in `--help` flag. While it’s possible to manually emulate help output, doing so quickly becomes custom, brittle, and repetitive across projects.

For some workflows, environment files are a reasonable choice. However, when developing a reusable PoC skeleton, especially one intended to be run repeatedly, shared, or revisited under time pressure. I found the lack of built-in help and the need for manual type conversion to be limiting. For those reasons, I ultimately preferred an explicit command-line interface built with `argparse`. 

Recall, we have a fictitious `uv` project in a directory labeled authrise. If you `cd` into that directory, and use an editor to build a file we'll call poc-args.py. The aim is to start building a workable PoC that we can reuse and doesn't rely on hard-coded values thus providing flexibility to any environment we will end up working in. Here's an example of the beginnings of a simple CLI with arguments.
```bash
uv run poc-args.py --target-ip 192.168.200.10 --target-port 5000 --listening-ip 192.168.1.5 --listening-port 9999
```

How would you configure such a script with a simple CLI like the above.

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="OSWE Application Exploit.")
    parser.add_argument("--target-ip", type=str, required=True, help="Input file path")
    parser.add_argument("--target-port", type=int, default=80, help="Input file path")
    parser.add_argument(
        "--listening-port",
        type=int,
        default=9001,
        help="Port to listen for reverse shell (default: 9001)",
    )
    parser.add_argument(
        "--listening-ip", type=str, help="IP to listen on for reverse shell"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Target IP: {args.target_ip}")
    print(f"Target Port: {args.target_port}")
    print(f"Listening IP: {args.listening_ip}")
    print(f"Listening Port: {args.listening_port}")


if __name__ == "__main__":
    main()

```

```bash
❯ uv run poc-args.py --target-ip 192.168.200.10 --target-port 5000 --listening-ip 192.168.1.5 --listening-port 9999
Target IP: 192.168.200.10
Target Port: 5000
Listening IP: 192.168.1.5
Listening Port: 9999
```


```bash
❯ uv run poc-args.py --help
usage: poc-args.py [-h] --target-ip TARGET_IP [--target-port TARGET_PORT] [--listening-port LISTENING_PORT]
                   [--listening-ip LISTENING_IP]

OSWE Application Exploit.

options:
  -h, --help            show this help message and exit
  --target-ip TARGET_IP
                        Input file path
  --target-port TARGET_PORT
                        Input file path
  --listening-port LISTENING_PORT
                        Port to listen for reverse shell (default: 9001)
  --listening-ip LISTENING_IP
                        IP to listen on for reverse shell
```

If you consider the content being presented in the case studies, one can figure out what might be good elements to consider for adding into a script as arguments. Some are fairly obvious like the target ip address and port, but some might not be, at least at first glance. Consider what kinds of elements might pop up repeatedly. 

A nice feature of argparse is that allows you to group arguments into sections. The `add_argument_group` method helps facilitate this. The grouping really helps when printing the options if you need a reminder of all the possible elements you can add as input. My grouping broke out into target options, attacker options, identity options, and the aptly named optional options. 

For target options, I considered the ip address, port, and a possible api port. I could have expanded this to have a api ip address if I desired. Attacker options centered around my Kali host and how I'd present say a reverse shell port or payload delivery using a web server to the victim. Identity options were configured to make use of my custom identity generator. There are options that allow me to reuse an existing configured user on the web application or set the password complexity, etc... 

Throughout the course, students will find they need to extract tokens using SQLi or have to generate tokens using various character sets. Maybe the character set might be restricted to just the alphabet or maybe just hex characters. To this end, I constructed a few character sets and included the ability to call on those character sets with a CLI option. As a result of these decisions, I ended up with a beginning skeleton PoC as presented below. Depending on your use case, what I've presented here may be too broad in scope, or maybe not enough.


```python
import argparse

CHARSETS = {
    "alpha": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "alnum": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "hex": "0123456789abcdef",
    "ascii": "".join(chr(i) for i in range(32, 127)),  # printable ASCII
    "symbols": "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~",
    "base64": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=",
    "numeric": "0123456789",
}


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
    target_group.add_argument(
        "--target-api-port",
        type=int,
        default=5000,
        help="Target API port (default: 5000)",
    )

    # --- Attacker options ---
    attacker_group = parser.add_argument_group("Attacker options")
    attacker_group.add_argument(
        "--listening-ip",
        type=str,
        default="127.0.0.1",
        help="IP to listen on for reverse shell (default: 127.0.0.1)",
    )
    attacker_group.add_argument(
        "--listening-port",
        type=int,
        default=9001,
        help="Port to listen for reverse shell (default: 9001)",
    )
    attacker_group.add_argument(
        "--payload-port",
        type=int,
        default=9999,
        help="Port to listen for xss or other payload (default: 9999)",
    )

    # --- Exploit options ---
    exploit_group = parser.add_argument_group("Exploit options")
    exploit_group.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Response delay in seconds for timing inference (default: 3)",
    )

    # --- Identity options ---
    identity_group = parser.add_argument_group("Identity options")
    identity_group.add_argument(
        "--user-file",
        type=str,
        default="user.json",
        help="Path to existing exploit user JSON (default: user.json)",
    )
    identity_group.add_argument(
        "--save-identity",
        type=str,
        help="Path to save newly generated identity JSON",
    )
    identity_group.add_argument(
        "--register",
        action="store_true",
        default=False,
        help="Whether the user has already been registered",
    )
    identity_group.add_argument(
        "--complexity", choices=["low", "medium", "high"], help="Password complexity"
    )
    identity_group.add_argument(
        "--include-address", action="store_true", help="Include street address"
    )
    identity_group.add_argument(
        "--include-phone", action="store_true", help="Include phone number"
    )

    optional_group = parser.add_argument_group("Optional options")
    optional_group.add_argument(
        "--charset",
        choices=CHARSETS.keys(),
        default="alnum",
        help="Charset to use for blind SQLi password extraction.",
    )
    optional_group.add_argument(
        "--proxy", default=None, help="Turn on Burp Suite proxy for debugging."
    )

    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Target IP: {args.target_ip}")
    print(f"Target Port: {args.target_port}")
    print(f"Listening IP: {args.listening_ip}")
    print(f"Listening Port: {args.listening_port}")


if __name__ == "__main__":
    main()

```

```python
❯ uv run poc.py --help
usage: poc.py [-h] --target-ip TARGET_IP [--target-port TARGET_PORT] [--target-api-port TARGET_API_PORT]
              [--listening-ip LISTENING_IP] [--listening-port LISTENING_PORT] [--payload-port PAYLOAD_PORT] [--delay DELAY]
              [--user-file USER_FILE] [--save-identity SAVE_IDENTITY] [--register] [--complexity {low,medium,high}]
              [--include-address] [--include-phone] [--charset {alpha,alnum,hex,ascii,symbols,base64,numeric}] [--proxy PROXY]

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

