from rest_framework_mongoengine.generics import RetrieveAPIView, UpdateAPIView
from .mongo_models import NotificationPreferences
from .serializers import NotificationPreferencesSerializer
from rest_framework.permissions import IsAuthenticated

class NotificationPreferenceListRetrieveAPIView(RetrieveAPIView):
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return NotificationPreferences.objects.get_or_create(user_id=user.id)[0]

class NotificationPreferenceUpdateAPIView(UpdateAPIView):
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return NotificationPreferences.objects.get_or_create(user_id=user.id)[0]