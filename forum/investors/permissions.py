from rest_framework.permissions import BasePermission
from users.permissions import get_token_payload_from_cookies


class InvestorSaveStartupPermission(BasePermission):
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        namespace = payload.get("name_space_name")
        return namespace == "investor"