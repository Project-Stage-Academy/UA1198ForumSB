from django.urls import path
import views


urlpatterns = [
    path("conversations/create", views.CreateConversationView.as_view(),
         name="create_conversation"),
    path("messages/send", views.SendMessageView.as_view(), name="send_message"),
    path("conversations/<int:conversation_id>/messages", views.MessagesListView.as_view(),
         name="conversation_messages")
]
