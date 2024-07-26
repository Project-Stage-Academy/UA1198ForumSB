from rest_framework.views import APIView


class CreateConversationView(APIView):
    def post(request):
        pass


class SendMessageView(APIView):
    def post(request):
        pass


class MessagesListView(APIView):
    def get(request, conversation_id):
        pass