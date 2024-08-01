class NotificationService:
    @staticmethod
    def mark_notification_as_read(notification, user_id):
        notification.update_one(
            __raw__={
                "$pull": {
                    "receivers": {"user_id": user_id}
                }
            }
        )