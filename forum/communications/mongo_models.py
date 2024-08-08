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


class Room(BaseTimestampModel):
    name = fields.StringField(max_length=128, unique=True, required=True)
    participants = fields.EmbeddedDocumentListField(NamespaceInfo, required=True, max_length=2)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name} participants={self.participants})"

    def __repr__(self):
        return str(self)


class Message(BaseTimestampModel):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    author = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    content = fields.StringField(required=True)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(room={self.room} author={self.author} "
            f"content={self.content})"
        )

    def __repr__(self):
        return str(self)
