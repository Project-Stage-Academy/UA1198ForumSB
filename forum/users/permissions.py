from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from investors.models import Investor
from projects.models import Project
from startups.models import Startup


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
    
    
def check_user_authenticated(request):
    if not request.user.is_authenticated:
        raise PermissionDenied({"error": "You have to be logged in."})


class BaseNamespacePermission(permissions.BasePermission):
    NAMESPACE = None

    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        if payload.get('name_space_name') != self.NAMESPACE:
            raise PermissionDenied({"error": f"Namespace is not {self.NAMESPACE}."})
        return True


class IsStartupNamespace(BaseNamespacePermission):
    NAMESPACE = 'startup'


class IsInvestorNamespace(BaseNamespacePermission):
    NAMESPACE = 'investor'
    
    
class BaseNamespaceSelectedPermission(permissions.BasePermission):
    NAMESPACE = None

    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        namespace_name = payload.get('name_space_name')
        namespace_id = payload.get('name_space_id')
        if namespace_name != self.NAMESPACE:
            raise PermissionDenied({"error": f"Namespace is not {self.NAMESPACE}."})
        if not namespace_id:
            raise PermissionDenied({"error": f"No {self.NAMESPACE} selected."})
        return True


class IsStartupNamespaceSelected(BaseNamespaceSelectedPermission):
    NAMESPACE = 'startup'


class IsInvestorNamespaceSelected(BaseNamespaceSelectedPermission):
    NAMESPACE = 'investor'


class IsNamespace(permissions.BasePermission):
    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        namespace = payload.get('name_space_name')
        if namespace not in ['startup', 'investor']:
            raise PermissionDenied({"error": "Invalid namespace."})
        return True
    
    
class IsMemberOfStartup(permissions.BasePermission):
    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get('user_id')
        namespace_id = payload.get('name_space_id')
        view_namespace_id = view.kwargs.get('pk')
        if not view_namespace_id:
            raise PermissionDenied({"error": "Namespace ID not provided in request."})
        if namespace_id != view_namespace_id:
            raise PermissionDenied({"error": "Namespace ID mismatch."})
        if not Startup.objects.filter(startup_id=view_namespace_id, user__user_id=user_id).exists():
            raise PermissionDenied({"error": "You are not a member of the specified startup."})    
        return True


class IsMemberOfInvestor(permissions.BasePermission):
    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get('user_id')
        namespace_id = payload.get('name_space_id')
        view_namespace_id = view.kwargs.get('pk')
        if not view_namespace_id:
            raise PermissionDenied({"error": "Namespace ID not provided in request."})
        if namespace_id != view_namespace_id:
            raise PermissionDenied({"error": "Namespace ID mismatch."})    
        if not Investor.objects.filter(investor_id=view_namespace_id, user__user_id=user_id).exists():
            raise PermissionDenied({"error": "You are not a member of the specified investor."})
        return True


class IsMemberOfNamespace(IsMemberOfStartup, IsMemberOfInvestor):
    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        namespace_name = payload.get('name_space_name')
        
        if namespace_name == 'investor':
            return IsMemberOfInvestor.has_permission(self, request, view)
        elif namespace_name == 'startup':
            return IsMemberOfStartup.has_permission(self, request, view)
        else:
            raise PermissionDenied({"error": "Invalid namespace."})


class IsMemberOfStartupProject(permissions.BasePermission):
    def has_permission(self, request, view):
        check_user_authenticated(request)
        payload = get_token_payload_from_cookies(request)
        user_id = payload.get('user_id')
        view_project_id = view.kwargs.get('pk')
        if not view_project_id:
            raise PermissionDenied({"error": "Project ID not provided in request."})
        project = get_object_or_404(Project, project_id=view_project_id)
        if project.startup.user.user_id != user_id:
            raise PermissionDenied({"error": 
                "You are not a member of the startup associated with this project."})
        return True


class ThisUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_id_from_url = int(request.get_full_path().split("users/")[1].split("/")[0])
        # access_token = request.COOKIES.get("access") after finished Sign In
        if request.headers.get('Authorization'):
            access_token = request.headers.get('Authorization').split('Bearer ')[1]
            access_token = AccessToken(access_token)
            current_user_id = access_token.payload.get('user_id')
            return current_user_id == user_id_from_url
        return False


class CanCreateNewNameSpacePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # access_token = request.COOKIES.get("access") after finished Sign In
        if request.headers.get('Authorization'):
            access_token = request.headers.get('Authorization').split('Bearer ')[1]
            access_token = AccessToken(access_token)
            return "name_space_id" not in access_token.payload
        return False