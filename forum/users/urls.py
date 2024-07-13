from django.urls import path
from rest_framework.throttling import ScopedRateThrottle

from users import views

app_name = 'users'

urlpatterns = [
    path('token/', views.TokenObtainPairView.as_view(throttle_classes=[ScopedRateThrottle]),
         name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(throttle_classes=[ScopedRateThrottle]),
         name='token_refresh'),
    path('select-namespace/', views.NamespaceSelectionView.as_view(), name='namespace_selection'),
    path('users/<int:user_id>/startups', views.UserStartupListView.as_view()),
    path('users/<int:user_id>/startups/<int:startup_id>', views.UserStartupDetailView.as_view()),
    path('users/<int:user_id>/startups/<int:startup_id>/projects',
         views.UserStartupProjectView.as_view()),
]
