from datetime import datetime
from enum import Enum

from mongoengine import Document, EmbeddedDocument, fields


class NamespaceEnum(Enum):
    STARTUP = "startup"
    INVESTOR = "investor"


class NamespaceInfo(EmbeddedDocument):
    user_id = fields.LongField()
    namespace = fields.EnumField(NamespaceEnum, required=True)
    namespace_id = fields.LongField()


class Notification(Document):
    initiator = fields.EmbeddedDocumentField(NamespaceInfo, required=True)
    receivers = fields.EmbeddedDocumentListField(NamespaceInfo)
    message = fields.StringField(required=True, max_length=255)
    created_at = fields.DateTimeField(default=datetime.now)


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
