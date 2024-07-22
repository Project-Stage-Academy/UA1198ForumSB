from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from bson import ObjectId
from bson.errors import InvalidId
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import NotificationSerializer

from communications.mongo_models import Notification


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all notifications for the authenticated user.",
        operation_summary="Retrieve user notifications",
        responses={
            200: NotificationSerializer(many=True),
            404: openapi.Response(description="Notifications not found.")
        }
    )
    def get(self, request):
        notifications = Notification.objects(receivers__user_id=request.user.user_id)
        
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
            400: openapi.Response(description="Invalid notification_id."),
            404: openapi.Response(description="Notification not found.")
        }
    )
    def put(self, request, notification_id):
        try:
            notification_id = ObjectId(notification_id)
        except InvalidId:
            return Response({"error": "Invalid notification_id."}, status=status.HTTP_400_BAD_REQUEST)

        notification = Notification.objects(pk=notification_id, receivers__user_id=request.user.user_id)
        if not notification:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
        notification_obj = notification.first()

        notification.update_one(
            __raw__={
                "$pull": {
                    "receivers": {"user_id": request.user.user_id}
                }
            }
        )
        
        serializer = NotificationSerializer(notification_obj)
        if not notification_obj.reload().receivers:
            notification_obj.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)
