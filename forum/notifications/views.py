from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.permissions import get_token_payload_from_cookies
from forum.config import ERROR_MESSAGES

from .serializers import NotificationSerializer

from communications.mongo_models import Notification
from notifications.services import NotificationService
from notifications.utils import extract_user_id_from_payload, validate_object_id


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all notifications for the authenticated user.",
        operation_summary="Retrieve user notifications",
        responses={
            200: NotificationSerializer(many=True),
            400: openapi.Response(description=ERROR_MESSAGES['BAD_REQUEST']),
        }
    )
    def get(self, request):
        payload = get_token_payload_from_cookies(request)
        user_id, error = extract_user_id_from_payload(payload)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
        notifications = Notification.objects(receivers__user_id=user_id)
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mark a notification as read by removing the user from the receivers list. \
        If no receivers are left, the notification is deleted.",
        operation_summary="Mark notification as read",
        responses={
            200: NotificationSerializer(),
            400: openapi.Response(description=ERROR_MESSAGES['BAD_REQUEST']),
            404: openapi.Response(description=ERROR_MESSAGES['NOTIFICATION_NOT_FOUND'])
        }
    )
    def put(self, request, notification_id):
        notification_id, error = validate_object_id(notification_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
        payload = get_token_payload_from_cookies(request)
        user_id, error = extract_user_id_from_payload(payload)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        notification = Notification.objects(pk=notification_id, receivers__user_id=user_id)
        if not notification:
            return Response({"error": ERROR_MESSAGES['NOTIFICATION_NOT_FOUND']}, status=status.HTTP_404_NOT_FOUND)
        notification_obj = notification.first()
        
        NotificationService.mark_notification_as_read(notification, user_id)
        
        serializer = NotificationSerializer(notification_obj)
        if not notification_obj.reload().receivers:
            notification_obj.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)
