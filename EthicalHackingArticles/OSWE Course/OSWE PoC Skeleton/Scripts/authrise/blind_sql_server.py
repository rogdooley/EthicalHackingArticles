import random
import string
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
state_lock = threading.Lock()

TOKEN_LENGTH = 16
CHARSET = string.ascii_letters + string.digits
SLEEP_DELAY = 0.2


def generate_token() -> str:
    token = "".join(random.choice(CHARSET) for _ in range(TOKEN_LENGTH))
    print(f"[server] new token: {token}")
    return token


current_token = generate_token()
hit_count = 0


@app.route("/probe", methods=["GET"])
def probe():
    """
    Timing oracle:
      /probe?pos=3&char=a
    Sleeps if token[pos] == char
    """
    pos = request.args.get("pos", type=int)
    char = request.args.get("char", type=str)

    if pos is None or char is None or len(char) != 1:
        return "bad request", 400

    with state_lock:
        global current_token, hit_count

        if pos < 0 or pos >= len(current_token):
            return "out of range", 404

        if current_token[pos] == char:
            time.sleep(SLEEP_DELAY)
            hit_count += 1

            # rotate token after two full client runs
            if hit_count >= 2 * TOKEN_LENGTH:
                print("[server] rotation threshold reached")
                current_token = generate_token()
                hit_count = 0

    return jsonify({"ok": True})


if __name__ == "__main__":
    # single-threaded server for correctness
    app.run(host="0.0.0.0", port=9001, threaded=False)
