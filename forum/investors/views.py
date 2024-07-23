from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Investor
from .serializers import InvestorSerializer, InvestorSaveStartupSerializer

from users.permissions import *
from rest_framework.permissions import IsAuthenticated
from .permissions import InvestorSaveStartupPermission


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
        InvestorSaveStartupPermission
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