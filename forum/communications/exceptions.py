
class BaseNotificationException(Exception):
    message: str = "Invalid notification provided"

    def __init__(self, message: str = "") -> None:
        self.message = message or self.__class__.message


class MessageTypeError(BaseNotificationException):
    message = "Field 'type' is invalid or non-existent"


class InvalidDataError(BaseNotificationException):
    message = "Invalid data provided"
