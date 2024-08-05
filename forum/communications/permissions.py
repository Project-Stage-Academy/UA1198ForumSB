from bson.objectid import ObjectId
from bson.errors import InvalidId
from rest_framework.permissions import BasePermission

from communications.mongo_models import Room
from users.permissions import get_token_payload_from_cookies


class IsParticipantOfConversation(BasePermission):
    """
        Custom permission to allow only participants of a room to access it
    """
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get("user_id")

        conversation_id = str(view.kwargs.get("conversation_id") or request.data.get("room"))
        if not conversation_id:
            return False
        
        try:
            conversation_id = ObjectId(conversation_id)
            conversation = Room.objects.get(id=conversation_id)
        except (InvalidId, Room.DoesNotExist):
            return False

        return any(participant.user_id == user_id for participant in conversation.participants)
    
    
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
        
        return participant_namespace == "investor" and \
            participant_namespace == namespace and \
            participant_id == user_id