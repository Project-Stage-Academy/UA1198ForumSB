from django.urls import reverse
import jwt
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView
)
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from forum import settings
from users.models import CustomUser
from users.serializers import UserRegisterSerializer
from users.utils import Util
from users.swagger_auto_schema_settings import *

class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'
    
    
class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Sending a confirmation email after successful validation of user data",
        operation_summary="User Registration",
        request_body=userRegisterView_request_body,
        responses=userRegisterView_responses,
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            token = RefreshToken()
            
            for key, value in user_data.items():
                token[key] = str(value)
            
            message_data = {
                'subject': 'Verify your email',
                'from_email': settings.EMAIL_HOST_USER,
                'to_email': user_data['email']
            }
            domain = get_current_site(request).domain
            verification_link = reverse('users:email-verify', kwargs={'token': str(token)})
            response = Util.send_email(domain, verification_link, message_data, user_data)
            if isinstance(response, Response):
                return response
            return Response("Verification link was sent to your email", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendEmailConfirmationView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Creating a new user after successful confirmation email",
        operation_summary="Confirmation Email",
        responses=sendEmailConfirmationView_responses,
    )
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT['ALGORITHM'])
            
            if CustomUser.objects.filter(email=payload['email']).exists():
                return Response({"Error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserRegisterSerializer(data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            return Response({"Error": "Verification link expired"}, status=status.HTTP_400_BAD_REQUEST)
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError):
            return Response({"Error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)