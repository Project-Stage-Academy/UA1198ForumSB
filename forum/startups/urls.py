from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StartupSizeViewSet, StartupViewSet

router = DefaultRouter()
router.register('startup_sizes', StartupSizeViewSet)
router.register('', StartupViewSet, basename='startup')


urlpatterns = [
    path('', include(router.urls))
]
