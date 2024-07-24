from rest_framework.permissions import BasePermission
from users.permissions import get_token_payload_from_cookies


class InvestorPermission(BasePermission):
    def has_permission(self, request, view):
        payload = get_token_payload_from_cookies(request)
        namespace = payload.get("name_space_name")
        return namespace == "investor"


class ThisInvestorPermission(InvestorPermission):

    def has_permission(self, request, view):
        """
        Check if investor_id of investor that make request matches to investor_id in request url
        """
        is_investor = super().has_permission(request, view)
        if not is_investor:
            return is_investor

        investor_id_from_url = view.kwargs.get("investor_id")
        payload = get_token_payload_from_cookies(request)
        current_investor_id = payload.get('name_space_id')
        return investor_id_from_url == current_investor_id
