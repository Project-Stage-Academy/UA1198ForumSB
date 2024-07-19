from os import environ

from django.apps import AppConfig

from mongoengine import connect


class CommunicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communications'

    def ready(self) -> None:
        connect(
            host=environ.get("FORUM_MONGO_HOST", "localhost"),
            port=int(environ.get("FORUM_MONGO_PORT", 27017)),
            db=environ.get("FORUM_MONGO_DB_NAME"),
            username=environ.get("FORUM_MONGO_USER_NAME"),
            password=environ.get("FORUM_MONGO_USER_PASSWORD")
        )
