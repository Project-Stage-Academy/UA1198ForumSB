from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .mongo_models import Room, Message
from .serializers import RoomSerializer, ChatMessageSerializer
from .utils import generate_room_name


class CreateConversationView(APIView):
    # TODO add permissions that allow only invetors initiate chat
    # TODO add permissions that allow to investor initiate chat only for itself

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
    # TODO add permissions that allow to investor/startup create message only for its room
    
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            new_message = Message(**serializer.data)
            new_message.save()
            # TODO call NotificationManager to send new_message.id
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class MessagesListView(APIView):
    def get(self, request, conversation_id):
        messages = Message.objects.filter(room = conversation_id)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)