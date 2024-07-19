#! /bin/env python

import json
import time
from os import environ

import requests
from dotenv import load_dotenv
from websocket import WebSocket

load_dotenv()


FORUM_HOST = environ.get("FORUM_HOST", "127.0.0.1")
FORUM_PORT = environ.get("FORUM_PORT", 8000)
FORUM_USER_EMAIL = environ.get("FORUM_USER_EMAIL")
FORUM_USER_PASSWORD = environ.get("FORUM_USER_PASSWORD")


def get_jwt_access() -> str:
    response = requests.post(
        f"http://{FORUM_HOST}:{FORUM_PORT}/users/token/",
        json={
            "email": FORUM_USER_EMAIL,
            "password": FORUM_USER_PASSWORD
        }
    )
    if response.status_code != 200:
        print("[-] Password auth failed")
        exit(0)

    access_token = response.json().get("access")
    if not access_token:
        print("[-] There is no access token in response JSON")
        exit(0)

    return access_token


def listen_for_notification(ws_client: WebSocket, timeout: float = 0.5):
    message_num = 1
    while True:
        data = json.loads(ws_client.recv())

        print(f"[{message_num}] {data}")
        ws_client.send(
            json.dumps(
                {
                    "type": "notification_ack",
                    "notification_id": data["notification_id"]
                }
            )
        )
        message_num += 1
        time.sleep(timeout)


if __name__ == "__main__":
    access_token = get_jwt_access()

    ws_client = WebSocket()
    ws_client.connect(
        f"ws://{FORUM_HOST}:{FORUM_PORT}/ws/notifications/",
        header=[
            f"Authorization: Bearer {access_token}"
        ]
    )

    listen_for_notification(ws_client)
