from bson.objectid import ObjectId
from bson.errors import InvalidId
from rest_framework.permissions import BasePermission

from communications.mongo_models import Room, NamespaceEnum
from users.permissions import get_token_payload_from_cookies


class IsParticipantOfConversation(BasePermission):
    """
        Custom permission to allow only participants of a room to access it
    """
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get("user_id")
        namespace_id = payload.get("name_space_id")
        namespace_name = payload.get("name_space_name")

        conversation_id = str(view.kwargs.get("conversation_id") or request.data.get("room"))
        if not conversation_id:
            return False
        
        try:
            conversation_id = ObjectId(conversation_id)
            conversation = Room.objects.get(id=conversation_id)
        except (InvalidId, Room.DoesNotExist):
            return False

        if any(participant.user_id == user_id and 
               participant.namespace_id == namespace_id and
               participant.namespace.value == namespace_name
               for participant in conversation.participants):
            return True
        return False


class IsInvestorInitiateChat(BasePermission):
    """
        Custom permission to allow only investors to initiate a chat
    """
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get("user_id")
        namespace = payload.get("name_space_name")
        participants = request.data.get("participants")
        if not participants:
            return False

        first_participant = participants[0]
        participant_namespace = first_participant.get("namespace")
        participant_id = first_participant.get("user_id")
        
        return (participant_namespace == NamespaceEnum.INVESTOR.value and
                participant_namespace == namespace and
                participant_id == user_id)


class IsAuthorOfMessage(BasePermission):
    """
        Custom permission to allow the authenticated user to send a message only 
        from their own account
    """
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get("user_id")
        namespace_id = payload.get("name_space_id")
        namespace_name = payload.get("name_space_name")
        
        author = request.data.get("author")
        
        if not author:
            return False

        author_user_id = author.get("user_id")
        author_namespace_id = author.get("namespace_id")
        author_namespace_name = author.get("namespace")

        return (author_user_id == user_id and
                author_namespace_id == namespace_id and
                author_namespace_name == namespace_name)