from datetime import datetime
from enum import Enum

from mongoengine import Document, EmbeddedDocument, fields, CASCADE


class BaseTimestampModel(Document):
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'abstract': True,
    }


class NamespaceEnum(Enum):
    STARTUP = "startup"
    INVESTOR = "investor"


class NotificationTypeEnum(Enum):
    ACCOUNT_ACTIVATION = "account_activation"
    PROFILE_UPDATE = "profile_update"
    PASSWORD_RESET = "password_reset"
    NEW_MESSAGE = "new_message"
    INVESTOR_SUBSCRIPTION = "investor_subscription"


class UserBaseModel(Document):
    user_id = fields.LongField(required=True)


class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField(required=True)
    namespace = fields.EnumField(NamespaceEnum, required=True)
    namespace_id = fields.LongField(required=True)


class Notification(BaseTimestampModel):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo, required=True)
    message = fields.StringField(required=True, max_length=255)


class NotificationTypes(EmbeddedDocument):
    name = fields.EnumField(NotificationTypeEnum, required=True)
    description = fields.StringField(max_length=255)


class NotificationPreferences(UserBaseModel):
    notification_types = fields.EmbeddedDocumentListField(
        fields.StringField(choices=[nt.value for nt in NotificationTypes]))
    ws_enabled = fields.BooleanField(default=True)
    email_enabled = fields.BooleanField(default=True)

    meta = {
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['notification_types.name']}
        ]
    }

    @classmethod
    def is_ws_enabled(cls, user_id, notification_type):
        preference = cls.objects(user_id=user_id, notification_types=notification_type.value).first()
        return preference.ws_enabled if preference else False

    @classmethod
    def is_email_enabled(cls, user_id, notification_type):
        preference = cls.objects(user_id=user_id, notification_types=notification_type.value).first()
        return preference.email_enabled if preference else False

    @classmethod
    def has_preferences(cls, user_id, notification_type):
        return cls.objects(user_id=user_id, notification_types_name=notification_type.value).first() is not None


class Room(BaseTimestampModel):
    name = fields.StringField(max_length=128, unique=True, required=True)
    participants = fields.EmbeddedDocumentListField(NamespaceInfo, required=True, max_length=2)


class Message(BaseTimestampModel):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    content = fields.StringField(required=True)
    author = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
