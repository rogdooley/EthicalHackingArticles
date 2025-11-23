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
