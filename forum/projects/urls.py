
from django.urls import path

from .views import TmpView
from .views import filter_projects, project_profile_update


urlpatterns = [
    path('', filter_projects),
    path('profile/', project_profile_update),
    path('test/', TmpView.as_view()),
]
