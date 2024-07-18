from django.urls import path
from rest_framework.throttling import ScopedRateThrottle
from users import views


app_name = 'users'

urlpatterns = [
    path(
        'token/',
        views.TokenObtainPairView.as_view(throttle_classes=[ScopedRateThrottle]),
        name='token_obtain_pair'
    ),
    path(
        'token/refresh/',
        views.TokenRefreshView.as_view(throttle_classes=[ScopedRateThrottle]),
        name='token_refresh'
    ),
    path(
        'password/reset',
        views.PasswordResetRequestView.as_view(),
        name='password_reset'
    ),
    path(
        'password/reset/confirm',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path(
        'email-verify/<str:token>/',
        views.SendEmailConfirmationView.as_view(),
        name='email-verify'
    ),
    path('logout/', views.LogoutAndBlacklistRefreshTokenView.as_view(), name='token_blacklist'), 
]
