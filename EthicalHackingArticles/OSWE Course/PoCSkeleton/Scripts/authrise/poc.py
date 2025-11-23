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
