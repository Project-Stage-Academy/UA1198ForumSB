from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StartupSizeViewSet

router = DefaultRouter()
router.register('startup_sizes', StartupSizeViewSet, 'startup_sizes')


urlpatterns = [
    path('', include(router.urls))
]