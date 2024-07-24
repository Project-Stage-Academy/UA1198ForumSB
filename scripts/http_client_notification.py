import requests
import json
from loguru import logger
from websocket_client import get_jwt_access, FORUM_HOST, FORUM_PORT


def get_notifications(access_token):
    response = requests.get(
        f"http://{FORUM_HOST}:{FORUM_PORT}/notifications/",
        headers={"Authorization": f"Bearer {access_token}"},
        cookies={"access_token": access_token}
    )
    if response.status_code == 200:
        logger.info("Notifications:")
        logger.info(json.dumps(response.json(), indent=4))
        return response.json()
    else:
        logger.error(f"Failed to get notifications: {response.status_code}")


def mark_notification_as_read(access_token, notification_id):
    response = requests.put(
        f"http://{FORUM_HOST}:{FORUM_PORT}/notifications/{notification_id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        cookies={"access_token": access_token}
    )
    if response.status_code == 200:
        logger.info("Notification marked as read:")
        logger.info(json.dumps(response.json(), indent=4))
    else:
        logger.error(f"Failed to mark notification as read: {response.status_code}")


if __name__ == "__main__":
    access_token = get_jwt_access()

    notifications = get_notifications(access_token)

    if notifications:
        first_notification_id = notifications[0]["id"]
        
        mark_notification_as_read(access_token, first_notification_id)
