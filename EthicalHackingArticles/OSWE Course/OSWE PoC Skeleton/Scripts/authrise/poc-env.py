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

    print(f"Target IP: {config['TARGET_IP']}")
    print(f"Target Port: {config['TARGET_PORT']}")
    print(f"Register new user: {config['REGISTER']}")
    print(f"Target IP: {config['TARGET_IP']}")
    print(f"Target Port: {config['TARGET_PORT']}")
    print(f"Listening IP: {config['LISTENING_IP']}")
    print(f"Listening Port: {config['LISTENING_PORT']}")


if __name__ == "__main__":
    main()
