import random
import string
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN_LEN = 24
SLEEP_TIME = 3
CHARSET = string.ascii_letters + string.digits

state = {
    "token": None,
    "requests": 0,
    "completed_methods": 0,
}


def new_token():
    return "".join(random.choice(CHARSET) for _ in range(TOKEN_LEN))


@app.before_request
def count_requests():
    state["requests"] += 1


@app.route("/vuln", methods=["POST"])
def vuln():
    """
    Expects JSON:
      {
        "pos": 5,
        "op": ">",
        "value": 77
      }
    Simulates:
      IF(ASCII(SUBSTRING(token, pos, 1)) > value, SLEEP(3), 0)
    """
    data = request.json
    pos = data["pos"]
    op = data["op"]
    value = data["value"]

    token = state["token"]

    if pos < 1 or pos > len(token):
        return jsonify(ok=True)

    c = ord(token[pos - 1])

    condition = {
        ">": c > value,
        "<": c < value,
        "=": c == value,
    }[op]

    if condition:
        time.sleep(SLEEP_TIME)

    return jsonify(ok=True)


@app.route("/length", methods=["POST"])
def length():
    """
    IF(LENGTH(token) > value, SLEEP(3), 0)
    """
    value = request.json["value"]
    if len(state["token"]) > value:
        time.sleep(SLEEP_TIME)
    return jsonify(ok=True)


@app.route("/done", methods=["POST"])
def done():
    state["completed_methods"] += 1
    return jsonify(ok=True)


@app.route("/reset", methods=["POST"])
def reset():
    state["token"] = new_token()
    state["requests"] = 0
    state["completed_methods"] = 0
    return jsonify(ok=True)


@app.route("/stats")
def stats():
    return jsonify(
        token=state["token"],
        requests=state["requests"],
    )


if __name__ == "__main__":
    state["token"] = new_token()
    print("[server] token:", state["token"])
    app.run(host="0.0.0.0", port=9001)
