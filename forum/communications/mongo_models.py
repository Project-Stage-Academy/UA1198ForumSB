from datetime import datetime

from mongoengine import Document, EmbeddedDocument, fields, CASCADE

class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField(required=True)
    namespace = fields.StringField(required=True)
    namespace_id = fields.LongField(required=True)


class Notification(Document):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo, required=True)
    message = fields.StringField(required=True, max_length=255)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    

class Room(Document):
    name = fields.StringField(max_length=128, unique=True, required=True)
    participants_id = fields.ListField(fields.IntField(), required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)


class Message(Document):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    namespace_id = fields.IntField(required=True)
    namespace_name = fields.StringField(required=True)
    content = fields.StringField(required=True)
    timestamp = fields.DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.room.update(updated_at=datetime.utcnow())
        super().save(*args, **kwargs)