import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from startups.models import Startup
from startups.serializers import StartupSerializer
from .models import Investor, InvestorStartup
from .serializers import InvestorSerializer, InvestorSaveStartupSerializer

from users.permissions import *
from rest_framework.permissions import IsAuthenticated
from .permissions import InvestorPermission, ThisInvestorPermission


INVESTOR_BASE_PERMISSIONS = [
    IsAuthenticated,
    ThisUserPermission,
    IsInvestorNamespaceSelected
]


class UserInvestorsView(APIView):
    permission_classes = INVESTOR_BASE_PERMISSIONS

    def get(self, request, user_id):
        investors = get_list_or_404(Investor, user=user_id)
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        serializer = InvestorSerializer(data={**request.data, 'user': user_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInvestorView(APIView):
    permission_classes = INVESTOR_BASE_PERMISSIONS+[
        ThisInvestor
    ]

    def get(self, request, user_id, investor_id):
        investor = get_object_or_404(Investor, user=user_id, investor_id=investor_id)
        serializer = InvestorSerializer(investor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id, investor_id):
        investor = get_object_or_404(Investor, user=user_id, investor_id=investor_id)
        serializer = InvestorSerializer(investor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, investor_id):
        investor = get_object_or_404(Investor, user=user_id, investor_id=investor_id)
        investor.is_deleted = True
        investor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvestorSaveStartupView(APIView):
    permission_classes = [
        IsAuthenticated,
        InvestorPermission
    ]

    def post(self, request, startup_id):
        payload = get_token_payload_from_cookies(request)
        investor_id = payload.get("name_space_id")
        investor_save_startup_data = {
            "investor_id": investor_id,
            "startup_id": startup_id
        }
        serializer = InvestorSaveStartupSerializer(data=investor_save_startup_data)
        if serializer.is_valid():
            serializer.save()
            return Response("The startup has been successfully saved.",
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestorSavedStartupsView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisInvestorPermission
    ]

    @swagger_auto_schema(
        operation_description="List of startups saved by the investor",
        operation_summary="Get list of startups",
        responses={
            status.HTTP_200_OK: StartupSerializer(),
            status.HTTP_400_BAD_REQUEST: 'BadRequest'
        }
    )
    def get(self, request, user_id, investor_id):
        order_by = request.query_params.get('order_by')
        filter_ = request.query_params.get('filter')

        if filter_:
            try:
                filter_data = json.loads(filter_)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid filter parameter'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            filter_data = {}

        startups = Startup.objects.filter(
            is_deleted=False,
            interested_investors__investor__investor_id=investor_id,
            interested_investors__investor__user_id=user_id
        )

        for key, value in filter_data.items():
            if key == 'size':
                lookup = key
            else:
                lookup = f'{key}__icontains'
            startups = startups.filter(**{lookup: value})

        if order_by:
            startups = startups.order_by(order_by)

        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnsaveStartupView(APIView):
    permission_classes = [
        IsAuthenticated,
        InvestorPermission
    ]

    @swagger_auto_schema(
        operation_description="Unfollow a startup by the investor",
        operation_summary="unfollow a startup",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_404_NOT_FOUND: 'NotFound'
        }
    )
    def delete(self, request, startup_id):
        payload = get_token_payload_from_cookies(request)
        investor_id = payload.get("name_space_id")
        try:
            startup = InvestorStartup.objects.get(startup_id=startup_id, investor_id=investor_id)
            startup.delete()
        except InvestorStartup.DoesNotExist:
            return Response({'error': 'Subscription is not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
