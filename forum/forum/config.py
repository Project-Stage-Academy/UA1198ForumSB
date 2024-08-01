from os import environ
from dotenv import load_dotenv

load_dotenv()


class EnvConfig:
    @staticmethod
    def get(key, default=None):
        value = environ.get(key, default)
        if value is None:
            raise ValueError(f"Environment variable '{key}' is not set")
        return value

    @staticmethod
    def mongo_host():
        return EnvConfig.get("FORUM_MONGO_HOST", "localhost")

    @staticmethod
    def mongo_port():
        try:
            return int(EnvConfig.get("FORUM_MONGO_PORT", 27017))
        except ValueError:
            raise ValueError("FORUM_MONGO_PORT must be an integer")

    @staticmethod
    def mongo_db_name():
        return EnvConfig.get("FORUM_MONGO_DB_NAME")

    @staticmethod
    def mongo_username():
        return EnvConfig.get("FORUM_MONGO_USER_NAME")

    @staticmethod
    def mongo_password():
        return EnvConfig.get("FORUM_MONGO_USER_PASSWORD")
    
    
ERROR_MESSAGES = {
    'INVALID_NOTIFICATION_ID': "Invalid notification ID.",
    'USER_ID_NOT_FOUND': "User ID not found in token payload.",
    'NOTIFICATION_NOT_FOUND': "Notification not found.",
    'BAD_REQUEST': "Bad request."
}
