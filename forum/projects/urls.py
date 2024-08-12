from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectHistoryViewSet, IndustryViewSet, ProjectSubscriptionView


router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'projects/(?P<project_id>\d+)/history', ProjectHistoryViewSet, basename='project-history')
router.register('industries', IndustryViewSet, 'industries')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:project_id>/subscribe/', ProjectSubscriptionView.as_view(), name="project-subscribe"),
]



