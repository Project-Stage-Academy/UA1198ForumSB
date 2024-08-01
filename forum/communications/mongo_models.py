from enum import Enum
from datetime import datetime

from mongoengine import Document, EmbeddedDocument, fields, CASCADE


class BaseTimestampModel(Document):
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'abstract': True,
    }
    
    
class NamespaceEnum(Enum):
    STARTUP = "startup"
    INVESTOR = "investor"
    

class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField(required=True)
    namespace = fields.EnumField(NamespaceEnum, required=True)
    namespace_id = fields.LongField(required=True)


class Notification(BaseTimestampModel):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo, required=True)
    message = fields.StringField(required=True, max_length=255)


class NotificationTypes(Document):
    name = fields.StringField(required=True, unique=True, max_length=50)
    description = fields.StringField(max_length=255)


class NotificationPreferences(Document):
    user_id = fields.LongField(required=True)
    notification_types = fields.EmbeddedDocumentListField(NotificationTypes)

    ws_enabled = fields.BooleanField(default=True)
    email_enabled = fields.BooleanField(default=True)

    @classmethod
    def is_ws_enabled(cls, user_id, notification_type_name):
        preference = cls.objects(user_id=user_id, notification_types_name=notification_type_name).first()
        return preference.ws_enabled if preference else False

    @classmethod
    def is_email_enabled(cls, user_id, notification_type_name):
        preference = cls.objects(user_id=user_id, notification_types_name=notification_type_name).first()
        return preference.email_enabled if preference else False

    @classmethod
    def has_preferences(cls, user_id, notification_type_name):
        return cls.objects(user_id=user_id, notification_types__name=notification_type_name).first() is not None


class Room(BaseTimestampModel):
    name = fields.StringField(max_length=128, unique=True, required=True)
    participants_id = fields.ListField(fields.IntField(), required=True)


class Message(BaseTimestampModel):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    namespace_id = fields.IntField(required=True)
    namespace_name = fields.StringField(required=True)
    content = fields.StringField(required=True)