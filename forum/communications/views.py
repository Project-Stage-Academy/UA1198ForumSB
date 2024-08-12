import json
from bson.objectid import ObjectId
from bson.errors import InvalidId
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .mongo_models import Room, Message, NamespaceEnum
from .serializers import RoomSerializer, ChatMessageSerializer
from .helpers import generate_room_name
from .permissions import IsAuthorOfMessage, IsInvestorInitiateChat, \
    IsParticipantOfConversation
from .utils import InvestorChatNotificationManager, StartupChatNotificationManager
from users.permissions import IsNamespace, get_token_payload_from_cookies
from startups.models import Startup
from investors.models import Investor

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
            logger.info(f"Conversation created: {new_room.id}")
            return Response(
                {**serializer.data, "id": str(new_room.id)},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationsListView(BaseAPIView):
    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def get(self, request):
        token_payload = get_token_payload_from_cookies(request)
        namespace = token_payload.get("name_space_name")
        namespace_id = token_payload.get("name_space_id")

        all_rooms = Room.objects.all()
        namespace_rooms = [room.to_json() for room in all_rooms if self.is_room_of_namespace(
            room, namespace, namespace_id
        )]
        json_data = json.dumps(namespace_rooms)

        return Response(data=json_data, status=status.HTTP_200_OK)
    
    @staticmethod
    def is_room_of_namespace(
        room: Room,
        namespace: str,
        namespace_id: int
    ) -> bool:
        return any([
            (namespace == participant["namespace"].value and 
                namespace_id == participant["namespace_id"])
            for participant in room.participants]
        )


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
            if new_message.author.namespace == NamespaceEnum.STARTUP:
                startup = get_object_or_404(
                    Startup, user_id=new_message.author.user_id, startup_id=new_message.author.namespace_id
                )
                manager = StartupChatNotificationManager(startup, new_message.room)
            elif new_message.author.namespace == NamespaceEnum.INVESTOR:
                investor = get_object_or_404(
                    Investor, user_id=new_message.author.user_id, investor_id=new_message.author.namespace_id
                )
                manager = InvestorChatNotificationManager(investor, new_message.room)
            notification_message = (
                f'Message: {new_message.id} was sent by {new_message.author.namespace} '
                f'with id {new_message.author.namespace_id}'
            )
            manager.push_notification(notification_message)
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
        messages = Message.objects.filter(room = conversation_id).to_json()
        logger.info(f"Messages retrieved for conversation: {conversation_id}")
        return Response(messages, status=status.HTTP_200_OK)


class MessageDetailView(APIView):
    def get(self, request, message_id):
        try:
            message_id = ObjectId(message_id)
        except InvalidId:
            return Response("Invalid message id", status=status.HTTP_400_BAD_REQUEST)
        message = Message.objects.filter(id=message_id).first()
        if not message:
            return Response("Message doesn't exist.", status=status.HTTP_404_NOT_FOUND)
        return Response(message.to_json(), status=status.HTTP_200_OK)
    
