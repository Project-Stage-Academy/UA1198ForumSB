from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from users.models import CustomUser
from users.serializers import NamespaceSerializer

class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'
    
class NamespaceSelectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token: str = request.COOKIES.get('refresh')
        
        if not refresh_token:
            return Response({"error": "Authentication credentials were not provided."}, 
                            status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            old_refresh_token = RefreshToken(refresh_token)
        except TokenError:
            return Response({"error": "Invalid or expired token."},
                            status=status.HTTP_401_UNAUTHORIZED)
             
        user_id = old_refresh_token.payload.get('user_id')
        user = get_object_or_404(CustomUser, user_id=user_id)

        serializer = NamespaceSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            namespace_id: int = serializer.validated_data['name_space_id']
            namespace_name: str = serializer.validated_data['name_space_name']

            old_refresh_token.blacklist()
            new_refresh_token = RefreshToken.for_user(user)
            new_refresh_token.payload.update({
                'name_space_id': namespace_id,
                'name_space_name': namespace_name
            })

            response = Response("Namespace has been successfully updated.", 
                                status=status.HTTP_200_OK)
            response.set_cookie(
                'refresh',
                new_refresh_token,
                httponly=True,
                secure=True,
                samesite='Strict',
            )
            response.set_cookie(
                'access',
                new_refresh_token.access_token,
                httponly=True,
                secure=True,
                samesite='Strict',
            )
            return response
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)