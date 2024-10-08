from django.urls import path
from . import views


urlpatterns = [
    path("conversations/create", views.CreateConversationView.as_view(), name="create_conversation"),
    path("conversations/", views.ConversationsListView.as_view(), name="conversations_list"),
    path("messages/send", views.SendMessageView.as_view(), name="send_message"),
    path("conversations/<str:conversation_id>/messages", views.MessagesListView.as_view(), name="conversation_messages"),
    path("messages/<str:message_id>", views.MessageDetailView.as_view(), name="message"),
]
