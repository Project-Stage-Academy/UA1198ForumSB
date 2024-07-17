from django.shortcuts import get_object_or_404
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
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from startups.models import Startup
from startups.serializers import StartupSerializer

from projects.models import Project
from projects.serializers import ProjectSerializer

from users.models import CustomUser
from users.serializers import NamespaceSerializer
from users.permissions import *
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


# This view has been created to test uesrs.permissions and can be deleted
class UserStartupProjectView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected,
        ThisStartup
    ]

    def get(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        serializer = StartupSerializer(project)
        return Response(serializer.data, status=200)

    def post(self, request, user_id, startup_id):
        serializer = StartupSerializer(data={
            **request.data,
            'user': user_id,
            'startup': startup_id
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        project.delete()
        return Response(status=204)
    

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
            email_sent = Util.send_email(domain, verification_link, message_data, user_data)
            if email_sent:
                return Response("Verification link was sent to your email", status=status.HTTP_200_OK)
            else:
                return Response({"error": "An error occurred during sending email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
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
                return Response({"error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserRegisterSerializer(data=payload)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            return Response({"error": "Verification link expired"}, status=status.HTTP_400_BAD_REQUEST)
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
