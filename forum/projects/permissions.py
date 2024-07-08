from rest_framework import permissions


class UpdateOwnProject(permissions.BasePermission):
    """
    
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.startup_id.user_id == request.user