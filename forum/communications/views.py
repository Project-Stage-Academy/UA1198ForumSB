from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .mongo_models import Room, Message
from .serializers import RoomSerializer, ChatMessageSerializer


class CreateConversationView(APIView):
    def post(request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            new_room = Room(**serializer.data)
            new_room.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SendMessageView(APIView):
    def post(request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            new_message = Message(**serializer.data)
            new_message.save()
            # TODO call NotificationManager to send new_message.id
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class MessagesListView(APIView):
    def get(request, conversation_id):
        messages = Message.objects.filter(room__id = conversation_id)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)