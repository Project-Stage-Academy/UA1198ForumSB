#! /bin/env python

import json
import time
from os import environ

import requests
from dotenv import load_dotenv
from loguru import logger
from websocket import WebSocket, WebSocketBadStatusException

load_dotenv()


FORUM_HOST = environ.get("FORUM_HOST", "127.0.0.1")
FORUM_PORT = environ.get("FORUM_PORT", 8000)
FORUM_USER_EMAIL = environ.get("FORUM_USER_EMAIL")
FORUM_USER_PASSWORD = environ.get("FORUM_USER_PASSWORD")


def get_jwt_access() -> str:
    logger.info("Starting password auth...")

    response = requests.post(
        f"http://{FORUM_HOST}:{FORUM_PORT}/users/token/",
        json={
            "email": FORUM_USER_EMAIL,
            "password": FORUM_USER_PASSWORD
        }
    )
    if response.status_code != 200:
        logger.error(f"Password auth failed. Unexpected status code '{response.status_code}'")
        exit(0)

    access_token = response.json().get("access")
    if not access_token:
        logger.error(f"There is no access token in JSON-response \n{response.json()}\n")
        exit(0)

    logger.info("Password auth was successful")

    return access_token


def listen_for_notification(ws_client: WebSocket, timeout: float = 0.5):
    logger.info("Waiting for notifications...")

    message_num = 1
    while True:
        data = json.loads(ws_client.recv())

        ws_client.send(
            json.dumps(
                {
                    "type": "notification_ack",
                    "notification_id": data["notification_id"]
                }
            )
        )
        logger.info(f"Notification: [{message_num}] {ws_client.recv()}")
        message_num += 1
        time.sleep(timeout)


if __name__ == "__main__":
    logger.info("Staring websocket client...")

    access_token = get_jwt_access()

    ws_client = WebSocket()
    try:
        ws_client.connect(
            f"ws://{FORUM_HOST}:{FORUM_PORT}/ws/notifications/",
            header=[
                f"Authorization: Bearer {access_token}"
            ]
        )
    except WebSocketBadStatusException as exc:
        logger.error(f"Failed to initiate websocket connection due to \n{exc}\n")
        exit(0)
    except Exception as exc:
        logger.error(f"Lol unexpected error) \n{exc}\n")
        exit(0)

    try:
        listen_for_notification(ws_client)
    except KeyboardInterrupt:
        logger.info("Bye-bye 🥺🥺🥺")
