from rest_framework import permissions

from users.permissions import get_token_payload_from_cookies


class UpdateOwnProject(permissions.BasePermission):
    """
    Allow updates only if the user owns the project
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        payload = get_token_payload_from_cookies(request)
        current_user_id = payload.get('user_id')
        return obj.startup.user_id == current_user_id
    