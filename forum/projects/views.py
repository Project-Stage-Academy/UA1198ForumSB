from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Industry
from .serializers import IndustrySerializer


class IndustryViewSet(GenericViewSet, ListModelMixin):
    queryset = Industry.objects.all()

    @swagger_auto_schema(
            responses={
                '200': IndustrySerializer
            }
    )
    def list(self, request, *args, **kwargs):
        return Response(
            IndustrySerializer(
                self.get_queryset(),
                many=True
            ).data
        )
