from os import environ

import jwt
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView as BaseTokenRefreshView,
)

from forum import settings
from forum.tasks import send_email_task
from forum.utils import build_email_message
from users.models import CustomUser
from users.permissions import *
from users.serializers import (
    CustomTokenRefreshSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
)
from users.swagger_auto_schema_settings import (
    sendEmailConfirmationView_responses,
    userRegisterView_request_body,
    userRegisterView_responses,
)

from .models import PasswordResetModel
from .serializers import (
    NamespaceSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserRegisterSerializer,
)
from .throttling import PasswordResetThrottle


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = authenticate(request, 
                            email=request.data.get('email'),
                            password=request.data.get('password'))
        if user:
            login(request, user)
        access_token = response.data.get('access')
        refresh_token = response.data.get('refresh')

        if access_token:
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=True
            )
        if refresh_token:
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=True
            )
        return response


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return JsonResponse({'detail': 'Refresh token not found in cookies'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie('access_token', serializer.validated_data['access'], httponly=True, secure=True)
        if 'refresh' in serializer.validated_data:
            response.set_cookie('refresh_token', serializer.validated_data['refresh'], httponly=True, secure=True)
        return response


class NamespaceSelectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token: str = request.COOKIES.get('refresh_token')
        
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
                'refresh_token',
                new_refresh_token,
                httponly=True,
                secure=True
            )
            response.set_cookie(
                'access_token',
                new_refresh_token.access_token,
                httponly=True,
                secure=True
            )
            return response
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []
    throttle_classes = [PasswordResetThrottle]

    def post(self, request: Request):
        serializer_data = self.serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)

        clear_data = serializer_data.validated_data

        user: CustomUser = get_object_or_404(CustomUser, email=clear_data['email'])

        token_generator = PasswordResetTokenGenerator()
        reset_token = token_generator.make_token(user)

        PasswordResetModel.objects.create(
            email=user,
            reset_token=reset_token
        )

        send_email_task.delay(
            subject="Password Reset Request",
            body=build_email_message(
                "email/password_reset_request.txt",
                {
                    "first_name": user.first_name,
                    "reset_link": environ.get('FORUM_PASSWORD_RESET_LINK') + reset_token
                }
            ),
            sender=settings.EMAIL_HOST_USER,
            receivers=[user.email],
        )

        return Response(
            {
                "detail": "The email with password reset link is sent to your email"
            }
        )


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = []
    throttle_classes = [PasswordResetThrottle]

    def post(self, request: Request, reset_token: str = None):
        serializer_data = self.serializer_class(data=request.data)
        serializer_data.is_valid(raise_exception=True)

        clear_data = serializer_data.validated_data

        reset_password_object = PasswordResetModel.objects.filter(
            reset_token=clear_data['reset_token']
        ).first()
        if not reset_password_object:
            raise NotFound(
                {
                    "detail": "Invalid reset token provided"
                }
            )

        user: CustomUser = get_object_or_404(
            CustomUser,
            email=reset_password_object.email
        )
        user.password = clear_data['password']
        user.save()

        reset_password_object.delete()

        return Response(
            {
                "detail": "Password successfully updated"
            }
        )


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

            domain = get_current_site(request).domain
            verification_link = reverse('users:email-verify', kwargs={'token': str(token)})
            
            send_email_task.delay(
                subject="Email Verification Request",
                body=build_email_message(
                    "email/email_confirmation_request.txt",
                    {
                        "first_name": user_data['first_name'],
                        "confirmation_email_link": domain + verification_link
                    }
                ),
                sender=settings.EMAIL_HOST_USER,
                receivers=[user_data['email']],
            )
            return Response("Verification link was sent to your email", status=status.HTTP_200_OK)
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


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data
        user = CustomUser.objects.get(email=user_data["email"])
        refresh = RefreshToken.for_user(user)
        data = {
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            }

        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie('access_token', str(refresh.access_token), httponly=False, secure=False)
        response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True)
        return response


class LogoutAndBlacklistRefreshTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response
        except Exception as e:
            return Response({"detail": "Token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
