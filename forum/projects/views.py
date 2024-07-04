from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# NOTE: this class created for testing proposes and will be deleted soon
class TmpView(APIView):
    @swagger_auto_schema(
        operation_description="Endpoint Operation Description",
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'field1': openapi.Schema(
                    type=openapi.TYPE_STRING, description="Field 1 Description"),
                'field2': openapi.Schema(
                    type=openapi.TYPE_STRING, description="Field 2 Description"),
            },
            required=['field1']
        )
    )
    def post(self, request):
        return Response("Success")


def filter_projects(request):
    ...


def project_profile_update(request):
    ...
