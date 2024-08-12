from rest_framework_mongoengine.generics import RetrieveAPIView, UpdateAPIView
from .mongo_models import NotificationPreferences
from .serializers import NotificationPreferencesSerializer
from rest_framework.permissions import IsAuthenticated
from mongoengine.errors import DoesNotExist

class NotificationPreferenceListRetrieveAPIView(RetrieveAPIView):
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            # Attempt to retrieve the existing notification preferences for the user
            return NotificationPreferences.objects.get(user_id=user.user_id)
        except DoesNotExist:
            # If preferences do not exist, create a new entry
            preferences = NotificationPreferences(user_id=user.user_id)
            preferences.save()
            return preferences

class NotificationPreferenceUpdateAPIView(UpdateAPIView):
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            # Attempt to retrieve the existing notification preferences for the user
            return NotificationPreferences.objects.get(user_id=user.user_id)
        except DoesNotExist:
            # If preferences do not exist, create a new entry
            preferences = NotificationPreferences(user_id=user.user_id)
            preferences.save()
            return preferences
