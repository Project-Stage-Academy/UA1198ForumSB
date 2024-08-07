from bson.errors import InvalidId
from bson.objectid import ObjectId
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import generate_room_name
from .mongo_models import Message, Room
from .serializers import ChatMessageSerializer, RoomSerializer


class CreateConversationView(APIView):
    # TODO add permissions that allow only invetors initiate chat
    # TODO add permissions that allow to investor initiate chat only for himself

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room_name = generate_room_name(serializer.data["participants"])
            room: Room | None = Room.objects(name=room_name).first()

            if not room:
                room = Room(name=room_name, **serializer.data)
                room.save()

            response_payload = serializer.data | {
                "conversation_id": str(room.pk)
            }
            return Response(
                response_payload,
                status=status.HTTP_201_CREATED
            )
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
            # TODO call NotificationManager to send new_message.id
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessagesListView(APIView):
    # TODO add permissions that allow to investor/startup view messages only of his room

    def get(self, request, conversation_id):
        try:
            conversation_id = ObjectId(conversation_id)
        except InvalidId:
            return Response("Invalid room id", status=status.HTTP_400_BAD_REQUEST)
        # TODO Add here pagination later
        messages = Message.objects.filter(room=conversation_id).to_json()
        return Response(messages, status=status.HTTP_200_OK)
