from datetime import datetime
from enum import Enum

from mongoengine import CASCADE, Document, EmbeddedDocument, fields


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
    meta = {
        'allow_inheritance': True,
    }


class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField(required=True)
    namespace = fields.EnumField(NamespaceEnum, required=True)
    namespace_id = fields.LongField(required=True)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(user_id={self.user_id} "
            f"namespace={self.namespace} namespace_id={self.namespace_id})"
        )

    def __repr__(self) -> str:
        return str(self)


class Notification(BaseTimestampModel):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo, required=True)
    message = fields.StringField(required=True, max_length=255)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(initiator={self.initiator} "
            f"receivers={self.receivers} message={self.message})"
        )

    def __repr__(self) -> str:
        return str(self)


class NotificationTypes(EmbeddedDocument):
    name = fields.EnumField(NotificationTypeEnum, required=True)
    description = fields.StringField(max_length=255)


class NotificationPreferences(UserBaseModel):
    notification_types = fields.EmbeddedDocumentListField(NotificationTypes)
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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name} participants={self.participants})"

    def __repr__(self):
        return str(self)


class Message(BaseTimestampModel):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    content = fields.StringField(required=True)
    author = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    content = fields.StringField(required=True)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(room={self.room} author={self.author} "
            f"content={self.content})"
        )

    def __repr__(self):
        return str(self)
