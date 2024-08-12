from django.urls import path
from .views import NotificationPreferenceListRetrieveAPIView, NotificationPreferenceUpdateAPIView

urlpatterns = [
    path('notifications/preferences/', NotificationPreferenceListRetrieveAPIView.as_view(),
         name='notification_preferences_list_retrieve'),
    path('notifications/preferences/update/', NotificationPreferenceUpdateAPIView.as_view(),
         name='notification_preferences_update'),
]