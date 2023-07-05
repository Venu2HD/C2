from flask_limiter.util import get_remote_address
from flask import Response, request, Flask
from flask_limiter import Limiter

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)
command_strings: list[str] = []
command_counts: list[int] = []


@app.route("/command-center", methods=["GET", "POST"])
def command_center() -> Response:
    if request.method == "GET":
        try:
            return Response(command_strings[0], 200)
        except IndexError:
            return Response("no commands to execute", 204)
    elif request.method == "POST":
        command = request.form.get("command")
        try:
            index = command_strings.index(command)
        except ValueError:
            return Response("command doesnt exist", 400)
        command_counts[index] -= 1
        if command_counts[index] == 0:
            del command_counts[index]
            del command_strings[index]
        return Response(f"ok, decremented {command}", 200)


@app.route("/key.txt", methods=["GET"])
def easter_egg() -> Response:
    return Response("Hey, what are you doing there?", 418)


@app.route("/check-key", methods=["GET"])
def web_check_key() -> Response:
    result = check_key(request.form.get("key"))
    if result:
        return Response("sucess", 200)
    else:
        return Response("invalid key", 429)


@app.route("/", methods=["GET"])
def home() -> str:
    with open("index.html", "r", encoding="utf-8") as index_file:
        return index_file.read()


@limiter.limit("30 seconds")
@app.route("/post", methods=["POST"])
def post() -> Response:
    key = request.args.get("key")
    command = request.args.get("command")
    amount = request.args.get("amount")

    try:
        amount = int(amount)
    except ValueError:
        return Response("amount is not a valid integer", 400)

    if check_key(key):
        command_strings.append(command)
        command_counts.append(amount)
        return Response("success", 200)
    else:
        return Response("invalid key", 429)


def check_key(key: str) -> bool:
    with open("key.txt", "r") as key_file:
        if key_file.read() == key:
            return True
    return False


def main() -> None:
    app.run("0.0.0.0", 80)


if __name__ == "__main__":
    main()
