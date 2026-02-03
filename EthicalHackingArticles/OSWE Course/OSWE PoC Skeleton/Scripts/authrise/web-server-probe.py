import random
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)

state_lock = threading.Lock()


def generate_secret():
    number = random.randint(0, 5000)
    new_secret = str(number).zfill(4)
    print(f"[-] current_secret {new_secret}")
    return new_secret


current_secret = generate_secret()
hit_count = 0


@app.route("/probe", methods=["GET"])
def probe():
    candidate = request.args.get("candidate")

    if not candidate or len(candidate) != 4:
        return "Parameter error", 404

    ip_address = request.remote_addr

    with state_lock:
        global current_secret, hit_count

        if candidate != current_secret:
            return "Parameter error", 404

        hit_count += 1
        print(f"[+] candidate found {candidate} from {ip_address} ({hit_count}/2)")

        if hit_count == 2:
            print("[+] hit limit reached, rotating secret")
            current_secret = generate_secret()
            hit_count = 0

        return jsonify({"message": "secret found"}), 200


if __name__ == "__main__":
    app.run(port=8000)
