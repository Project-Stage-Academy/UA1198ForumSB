from django.urls import path
from rest_framework.throttling import ScopedRateThrottle

from startups.views import UserStartupsView, UserStartupView
from users import views

app_name = 'users'

urlpatterns = [
    path('token/', views.TokenObtainPairView.as_view(throttle_classes=[ScopedRateThrottle]),
         name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(throttle_classes=[ScopedRateThrottle]),
         name='token_refresh'),
    path('<int:user_id>/startups/', UserStartupsView.as_view(), name='user_startups'),
    path('<int:user_id>/startups/<int:startup_id>/', UserStartupView.as_view(), name='user_startup'),
]
