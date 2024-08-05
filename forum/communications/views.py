from bson.objectid import ObjectId
from bson.errors import InvalidId
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .mongo_models import Room, Message
from .serializers import RoomSerializer, ChatMessageSerializer
from .helpers import generate_room_name
from .permissions import IsInvestorInitiateChat, IsParticipantOfConversation
from users.permissions import IsNamespace


CONVERSATION_BASE_PERMISSIONS = [
    IsAuthenticated,
    IsNamespace
]


class CreateConversationView(APIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS + [
        IsInvestorInitiateChat
    ]

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room_name = generate_room_name(serializer.data["participants"])
            new_room = Room(name=room_name, **serializer.data)
            new_room.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationsListView(APIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS

    def get(self, request):
        pass


class SendMessageView(APIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS + [
        IsParticipantOfConversation
    ]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            new_message = Message(**serializer.data)
            new_message.save()
            # TODO call NotificationManager to send new_message.id
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessagesListView(APIView):
    permission_classes = CONVERSATION_BASE_PERMISSIONS + [
        IsParticipantOfConversation
    ]

    def get(self, request, conversation_id):
        try:
            conversation_id = ObjectId(conversation_id)
        except InvalidId:
            return Response("Invalid room id", status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(room = conversation_id).to_json()
        return Response(messages, status=status.HTTP_200_OK)