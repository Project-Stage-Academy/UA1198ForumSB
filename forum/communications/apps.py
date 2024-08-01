import logging

from django.apps import AppConfig
from forum.config import EnvConfig

from mongoengine import connect

from forum.logging import logger


class CommunicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communications'

    def ready(self) -> None:
        try:
            connect(
                host=EnvConfig.mongo_host(),
                port=EnvConfig.mongo_port(),
                db=EnvConfig.mongo_db_name(),
                username=EnvConfig.mongo_username(),
                password=EnvConfig.mongo_password()
            )
        except ConnectionError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")