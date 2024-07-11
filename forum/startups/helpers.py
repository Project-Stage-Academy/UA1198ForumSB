from .models import Startup
from projects.models import Project, Industry
from django.db.models import Q


def select_startups_by_search_string(search_string):
    return Startup.objects.filter(
        Q(name__icontains = search_string) |
        Q(location__icontains = search_string) |
        Q(description__icontains = search_string)
    )


def filter_startups(query_params):
    industry_name = query_params.get("industry")
    max_budget = query_params.get("max-budget")
    size = query_params.get("size")
    
    startups = Startup.objects.filter()

    if industry_name:
        industry = Industry.objects.filter(name=industry_name).first()
        projects = Project.objects.filter(industries=industry)
        startups_ids = list(map(lambda proj: proj.startup.startup_id, projects))
        startups = startups.filter(pk__in=startups_ids)
    
    if max_budget:
        try:
            max_budget = int(max_budget)
        except ValueError:
            return []
        projects = Project.objects.filter(budget__lte=max_budget)
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