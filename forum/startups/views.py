from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.response import Response
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema

from .models import StartupSize, Startup
from .serializers import StartupSizeSerializer, StartupSerializer

from projects.models import Project, Industry
from projects.serializers import ProjectSerializer, IndustrySerializer


class StartupSizeViewSet(GenericViewSet, ListModelMixin):
    queryset = StartupSize.objects.all()

    @swagger_auto_schema(
            responses={
                '200': StartupSizeSerializer
            }
    )
    def list(self, request, *args, **kwargs):
        return Response(
            StartupSizeSerializer(
                self.get_queryset(),
                many=True
            ).data
        )


def select_startups_by_search_string(search_string):
    return Startup.objects.filter(
        Q(name__icontains = search_string) |
        Q(location__icontains = search_string) |
        Q(description__icontains = search_string)
    )


def filter_startups(query_params):
    industry_name = query_params.get("industry")
    budget = query_params.get("budget")
    size = query_params.get("size")
    
    startups = Startup.objects.filter()

    if industry_name:
        industry = Industry.objects.filter(name=industry_name).first()
        projects = Project.objects.filter(industries=industry)
        startups_ids = list(map(lambda proj: proj.startup.startup_id, projects))
        startups = startups.filter(pk__in=startups_ids)

    if size:
        try:
            size = int(size)
        except ValueError:
            return []
        startups = startups.filter(
            Q(size__people_count_min__lte=size) &
            Q(size__people_count_max__gt=size)
        )
        
    return startups


class StartupViewSet(ViewSet):
    def list(self, request):
        search_string = request.query_params.get('search')
        if search_string:
            startups = select_startups_by_search_string(search_string)
        elif request.query_params:
            startups = filter_startups(request.query_params)
        else:
            startups = Startup.objects.all()
        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data, status=200)
    
    def retrieve(self, request, pk):
        try:
            startup = Startup.objects.get(startup_id=pk)
        except Startup.DoesNotExist:
            return Response(status=404)
        
        startup_serializer = StartupSerializer(startup)
        response = startup_serializer.data

        project = Project.objects.filter(startup=startup).first()
        if project:
            project_serializer = ProjectSerializer(project)
            response = {
                **response,
                "project": project_serializer.data
            }
            industries = Industry.objects.filter(projects=project)
            if len(industries):
                industries_serializer = IndustrySerializer(industries, many=True)
                response = {
                    **response,
                    "industries": industries_serializer.data
                }

        return Response(response, status=200)