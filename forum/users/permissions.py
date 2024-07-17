from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from rest_framework.exceptions import PermissionDenied


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


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
    """
        Check what namespace has been selected: startup or investor
    """
    NAMESPACE = None

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS + ['POST']:
            return True
        
        payload = get_token_payload_from_cookies(request)
        namespace_name = payload.get('name_space_name')
        return namespace_name == self.NAMESPACE


class IsStartupNamespaceSelected(BaseNamespaceSelectedPermission):
    NAMESPACE = 'startup'


class IsInvestorNamespaceSelected(BaseNamespaceSelectedPermission):
    NAMESPACE = 'investor'
    
    
class ThisNamespace(permissions.BasePermission):
    """
        Check if namespace_id of selected namespace matches to namespace_id in request url
    """
    NAMESPACE = None

    def has_permission(self, request, view):
        if request.method in ["PUT", "PATCH"]:
            payload = get_token_payload_from_cookies(request)
            namespace_id = payload.get('name_space_id')
            view_namespace_id = view.kwargs.get(f'{self.NAMESPACE}_id')
            return namespace_id == view_namespace_id
        return True
    
    
class ThisStartup(ThisNamespace):
    NAMESPACE = 'startup'


class ThisInvestor(ThisNamespace):
    NAMESPACE = 'investor'


class ThisUserPermission(permissions.BasePermission):
    """
        Check if user_id of user that make request matches to user_id in request url
    """
    def has_permission(self, request, view):
        user_id_from_url = view.kwargs.get("user_id")
        payload = get_token_payload_from_cookies(request)
        current_user_id = payload.get('user_id')
        return current_user_id == user_id_from_url
