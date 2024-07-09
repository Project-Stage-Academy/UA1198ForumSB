from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from users.models import CustomUser
from .models import PasswordResetModel
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer
)


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []

    def post(self, request: Request):
        serializer_data = self.serializer_class(data=request.data)
        if not serializer_data.is_valid():
            raise ValidationError()

        clear_data = serializer_data.validated_data

        user = CustomUser.objects.filter(
            email__iexact=clear_data['email']
        ).first()

        if not user:
            raise NotFound(detail="User with such email is not exists")

        token_generator = PasswordResetTokenGenerator()
        reset_token = token_generator.make_token(user)

        PasswordResetModel.objects.create(
            email=clear_data['email'],
            reset_token=reset_token
        )


#        send_mail()

        return Response(
            {
                "detail": "The email with password reset link is sent to your email"
            }
        )


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = []

    def post(self, request: Request, reset_token: str = None):
        serializer_data = self.serializer_class(data=request.data)
        if not serializer_data.is_valid():
            raise ValidationError()

        clear_data = serializer_data.validated_data

        reset_password_object = PasswordResetModel.objects.filter(
            reset_token=clear_data['reset_token']
        ).first()
        if not reset_password_object:
            raise NotFound()

        user = CustomUser.objects.get(email=reset_password_object.email)
        user.password = clear_data['password']
        user.save()

        reset_password_object.delete()

        return Response(
            {
                "detail": "Password successfully updated"
            }
        )
