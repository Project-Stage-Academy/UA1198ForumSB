from django.urls import path
from rest_framework.throttling import ScopedRateThrottle

from investors.views import UserInvestorsView, UserInvestorView
from startups.views import UserStartupsView, UserStartupView

from users import views


app_name = 'users'

urlpatterns = [
    path('select-namespace/', views.NamespaceSelectionView.as_view(), name='namespace_selection'),
    path('<int:user_id>/investors/', UserInvestorsView.as_view(), name='user_investors'),
    path('<int:user_id>/investors/<int:investor_id>/', UserInvestorView.as_view(), name='user_investor'),
    path('<int:user_id>/startups/', UserStartupsView.as_view(), name='user_startups'),
    path('<int:user_id>/startups/<int:startup_id>/', UserStartupView.as_view(), name='user_startup'),
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

    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.LogoutAndBlacklistRefreshTokenView.as_view(), name='token_blacklist'),
]
