import logging
from bson import ObjectId
from bson.errors import InvalidId

from communications.mongo_models import NamespaceEnum
from forum.config import ERROR_MESSAGES

URL_PATTERNS = {
    'startup': '/users/{user_id}/startups/{namespace_id}/',
    'investor': '/users/{user_id}/investors/{namespace_id}/',
}

logger = logging.getLogger("django")


class URLGenerator:
    @staticmethod
    def generate_url(namespace: str, **kwargs) -> str | None:
        try:
            namespace_value = NamespaceEnum(namespace).name.lower()
            pattern = URL_PATTERNS.get(namespace_value)
            if pattern:
                return pattern.format(**kwargs)
        except ValueError:
            logger.error(f"Invalid namespace: {namespace}")
        except KeyError as e:
            logger.error(f"Missing key for URL pattern: {e}")
        return None
    
    
def validate_object_id(object_id):
    try:
        return ObjectId(object_id), None
    except InvalidId:
        return None, ERROR_MESSAGES['INVALID_NOTIFICATION_ID']


def extract_user_id_from_payload(payload):
    user_id = payload.get('user_id')
    if not user_id:
        return None, ERROR_MESSAGES['USER_ID_NOT_FOUND']
    return user_id, None