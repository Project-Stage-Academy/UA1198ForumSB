from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken


class ThisUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_id_from_url = int(request.get_full_path().split("users/")[1].split("/")[0])
        # access_token = request.COOKIES.get("access")
        if request.headers.get('Authorization'):
            access_token = request.headers.get('Authorization').split('Bearer ')[1]
            access_token = AccessToken(access_token)
            current_user_id = access_token.payload.get('user_id')
            return current_user_id == user_id_from_url
        return False