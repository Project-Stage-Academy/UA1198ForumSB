from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .mongo_models import Room, Message, NamespaceEnum
from .serializers import RoomSerializer, ChatMessageSerializer
from .helpers import generate_room_name
from .utils import InvestorChatNotificationManager, StartupChatNotificationManager
from startups.models import Startup
from investors.models import Investor
from bson.objectid import ObjectId
from bson.errors import InvalidId


class CreateConversationView(APIView):
    # TODO add permissions that allow only invetors initiate chat
    # TODO add permissions that allow to investor initiate chat only for himself

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room_name = generate_room_name(serializer.data["participants"])
            new_room = Room(name=room_name, **serializer.data)
            new_room.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationsListView(APIView):
    def get(self, request):
        pass


class SendMessageView(APIView):
    # TODO add permissions that allow to investor/startup create message only for his room

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            new_message = Message(**serializer.data)
            new_message.save()
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


class MessagesListView(APIView):
    # TODO add permissions that allow to investor/startup view messages only of his room

    def get(self, request, conversation_id):
        try:
            conversation_id = ObjectId(conversation_id)
        except InvalidId:
            return Response("Invalid room id", status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(room = conversation_id).to_json()
        return Response(messages, status=status.HTTP_200_OK)