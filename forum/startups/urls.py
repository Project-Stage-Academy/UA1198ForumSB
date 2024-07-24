from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StartupSizeViewSet, StartupViewSet
from investors.views import InvestorSaveStartupView, UnsaveStartupView

router = DefaultRouter()
router.register('', StartupViewSet, basename='startup')
router.register('startup_sizes', StartupSizeViewSet, 'startup_sizes')


urlpatterns = [
    path('', include(router.urls)),
    path('<int:startup_id>/save', InvestorSaveStartupView.as_view(), name="save_startup"),
    path('<int:startup_id>/unsave/', UnsaveStartupView.as_view(), name='unsave_startup')
]
