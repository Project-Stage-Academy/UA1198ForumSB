from bson.errors import InvalidId
from bson.objectid import ObjectId
from django.shortcuts import get_object_or_404
from investors.models import Investor
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from startups.models import Startup

from .helpers import generate_room_name
from .mongo_models import Message, NamespaceEnum, Room
from .serializers import ChatMessageSerializer, RoomSerializer
from .utils import InvestorChatNotificationManager, StartupChatNotificationManager


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
            if new_message.author.namespace == NamespaceEnum.STARTUP:
                startup = get_object_or_404(
                    Startup,
                    user_id=new_message.author.user_id,
                    startup_id=new_message.author.namespace_id
                )
                manager = StartupChatNotificationManager(startup, new_message.room)
            elif new_message.author.namespace == NamespaceEnum.INVESTOR:
                investor = get_object_or_404(
                    Investor,
                    user_id=new_message.author.user_id,
                    investor_id=new_message.author.namespace_id
                )
                manager = InvestorChatNotificationManager(investor, new_message.room)

            notification_message = (
                f'Message: {new_message.id} was sent by {new_message.author.namespace} '
                f'with id {new_message.author.namespace_id}'
            )
            manager.push_notification(
                notification_message,
                message_id=str(new_message.pk)
            )

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
        return Response(messages, status=status.HTTP_200_OK)
