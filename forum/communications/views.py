from bson.objectid import ObjectId
from bson.errors import InvalidId
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .mongo_models import Room, Message
from .serializers import RoomSerializer, ChatMessageSerializer
from .helpers import generate_room_name
from .permissions import IsAuthorOfMessage, IsInvestorInitiateChat, \
    IsParticipantOfConversation
from users.permissions import IsNamespace
from forum.logging import logger 


CONVERSATION_BASE_PERMISSIONS = [
    IsAuthenticated,
    IsNamespace
]


class BaseAPIView(APIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS

    def handle_exception(self, exc):
        if isinstance(exc, Ratelimited):
            return JsonResponse({"detail": "Too many requests"},
                                status=status.HTTP_429_TOO_MANY_REQUESTS)
        return super().handle_exception(exc)


class CreateConversationView(BaseAPIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS + [
        IsInvestorInitiateChat
    ]

    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room_name = generate_room_name(serializer.data["participants"])
            new_room = Room(name=room_name, **serializer.data)
            new_room.save()
            logger.info(f"Conversation created: {new_room.name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationsListView(BaseAPIView):
    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def get(self, request):
        pass


class SendMessageView(BaseAPIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS + [
        IsParticipantOfConversation,
        IsAuthorOfMessage
    ]

    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            new_message = Message(**serializer.data)
            new_message.save()
            logger.info(f"Message sent: {new_message.id}")
            # TODO call NotificationManager to send new_message.id
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessagesListView(BaseAPIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS + [
        IsParticipantOfConversation
    ]

    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def get(self, request, conversation_id):
        try:
            conversation_id = ObjectId(conversation_id)
        except InvalidId:
            return Response("Invalid room id", status=status.HTTP_400_BAD_REQUEST)
        # TODO Add here pagination later        
        messages = Message.objects.filter(room=conversation_id).to_json()
        logger.info(f"Messages retrieved for conversation: {conversation_id}")
        return Response(messages, status=status.HTTP_200_OK)