from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StartupSizeViewSet, StartupViewSet

router = DefaultRouter()
router.register('', StartupViewSet, basename='startup')
router.register('startup_sizes', StartupSizeViewSet, 'startup_sizes')


urlpatterns = [
    path('', include(router.urls))
]
