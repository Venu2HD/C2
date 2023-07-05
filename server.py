from flask_limiter.util import get_remote_address
from flask import Response, request, Flask
from flask_limiter import Limiter
from threading import Thread
from hashlib import sha256
from time import sleep

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)
command_strings: list[str] = []
command_counts: list[int] = []
images: list[bytes] = []


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


@app.route("/image-center", methods=["GET"])
def image_center() -> Response:
    if request.method == "GET":
        try:
            return images[0]
        except IndexError:
            return Response("no images to show", 204)


@app.route("/key.txt", methods=["GET"])
def easter_egg() -> Response:
    return Response("Hey, what are you doing there?", 418)


@app.route("/", methods=["GET"])
def home() -> str:
    with open("index.html", "r", encoding="utf-8") as index_file:
        return index_file.read()


@app.route("/post_image", methods=["POST"])
def post_image() -> Response:
    if check_key(request.args.get("key")):
        data = request.files["image"].stream.read()
        Thread(target=post_image_thread, args=[data]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


def post_image_thread(data: bytes) -> None:
    images.append(data)
    sleep(9)
    images.remove(data)


@app.route("/post_command", methods=["POST"])
def post_command() -> Response:
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
        return Response("invalid key", 403)


def hash_key(key: str) -> str:
    return sha256(key.encode()).hexdigest()


def check_key(key: str) -> bool:
    with open("key.txt", "r") as key_file:
        if key_file.read() == hash_key(key):
            return True
    return False


def main() -> None:
    app.run("0.0.0.0", 80)


if __name__ == "__main__":
    main()
