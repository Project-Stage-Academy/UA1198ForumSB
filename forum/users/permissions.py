from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from rest_framework.exceptions import PermissionDenied


def get_token_payload_from_cookies(request):
    token = request.COOKIES.get('access')
    if not token:
        raise PermissionDenied({"error": "Authentication credentials were not provided."})
    try:
        token_obj = AccessToken(token)
        payload = token_obj.payload
    except TokenError:        
        raise PermissionDenied({"error": "Invalid or expired token."})
    if not payload:
        raise PermissionDenied({"error": "Token payload is missing."})
    return payload
    
    
class BaseNamespaceSelectedPermission(permissions.BasePermission):
    NAMESPACE = None

    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        namespace_name = payload.get('name_space_name')
        if namespace_name != self.NAMESPACE:
            raise PermissionDenied({"error": f"Namespace is not {self.NAMESPACE}."})
        namespace_id = payload.get('name_space_id')
        if not namespace_id:
            raise PermissionDenied({"error": f"No {self.NAMESPACE} selected."})
        return True


class IsStartupNamespaceSelected(BaseNamespaceSelectedPermission):
    NAMESPACE = 'startup'


class IsInvestorNamespaceSelected(BaseNamespaceSelectedPermission):
    NAMESPACE = 'investor'


class IsNamespace(permissions.BasePermission):
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        namespace = payload.get('name_space_name')
        if namespace not in ['startup', 'investor']:
            raise PermissionDenied({"error": "Invalid namespace."})
        return True


class ThisNamespace(permissions.BasePermission):
    NAMESPACE = None

    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        namespace_id = payload.get('name_space_id')
        view_namespace_id = view.kwargs.get(f'{self.NAMESPACE}_id')
        if namespace_id != view_namespace_id:
            raise PermissionDenied({"error": "Namespace ID mismatch."})   
        return True
    
    
class ThisStartup(ThisNamespace):
    NAMESPACE = 'startup'


class ThisInvestor(ThisNamespace):
    NAMESPACE = 'investor'


class ThisUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if request.method in ["PUT", "Pat"]:
            pass
        user_id_from_url = int(request.get_full_path().split("users/")[1].split("/")[0])
        # access_token = request.COOKIES.get("access") after finished Sign In
        if request.headers.get('Authorization'):
            access_token = request.headers.get('Authorization').split('Bearer ')[1]
            access_token = AccessToken(access_token)
            current_user_id = access_token.payload.get('user_id')
            return current_user_id == user_id_from_url
        return False


class NameSpaceIsNotSelected(permissions.BasePermission):
    def has_permission(self, request, view):
        # access_token = request.COOKIES.get("access") after finished Sign In
        if request.headers.get('Authorization'):
            access_token = request.headers.get('Authorization').split('Bearer ')[1]
            access_token = AccessToken(access_token)
            return "name_space_id" not in access_token.payload
        return False