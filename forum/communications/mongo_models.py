from datetime import datetime

from mongoengine import Document, EmbeddedDocument, fields, CASCADE

class BaseTimestampModel(Document):
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'abstract': True,
    }
    

class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField(required=True)
    namespace = fields.StringField(required=True)
    namespace_id = fields.LongField(required=True)


class Notification(BaseTimestampModel):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo, required=True)
    message = fields.StringField(required=True, max_length=255)
    

class Room(BaseTimestampModel):
    name = fields.StringField(max_length=128, unique=True, required=True)
    participants_id = fields.ListField(fields.IntField(), required=True)


class Message(BaseTimestampModel):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    namespace_id = fields.IntField(required=True)
    namespace_name = fields.StringField(required=True)
    content = fields.StringField(required=True)