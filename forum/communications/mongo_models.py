from datetime import datetime

from mongoengine import Document, EmbeddedDocument, fields, CASCADE

class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField()
    namespace = fields.StringField(required=True)
    namespace_id = fields.LongField()


class Notification(Document):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo)
    message = fields.StringField(required=True, max_length=255)
    created_at = fields.DateTimeField(default=datetime.now)
    

class Room(Document):
    name = fields.StringField(max_length=128, unique=True, required=True)
    participants_id = fields.ListField(fields.IntField(), required=True)
    created_at = fields.DateTimeField(default=datetime.now)
    updated_at = fields.DateTimeField(default=datetime.now)


class Message(Document):
    room = fields.ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    namespace_id = fields.IntField(required=True)
    namespace_name = fields.StringField(required=True)
    content = fields.StringField(required=True)
    timestamp = fields.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.room.update(updated_at=datetime.now())
        super().save(*args, **kwargs)


# Notification schema
# {
#     "initiator": {
#         "namespace": "",
#         "namespace_id": 0
#     },
#     "receivers": [
#         {
#             "namespace": "",
#             "namespace_id": 0
#         },
#         {
#             "namespace": "",
#             "namespace_id": 0
#         }
#     ],
#     "message": "",
#     "created_at": ""
# }
