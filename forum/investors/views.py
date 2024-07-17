from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Investor
from .serializers import InvestorSerializer

from users.permissions import *
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class UserInvestorsView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsInvestorNamespaceSelected
    ]

    def get(self, request, user_id):
        investors = get_list_or_404(Investor, user=user_id)
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, user_id):
        serializer = InvestorSerializer(data={**request.data, 'user': user_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserInvestorView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsInvestorNamespaceSelected,
        ThisInvestor
    ]

    def get(self, request, user_id, investor_id):
        investor = get_object_or_404(Investor, user=user_id, investor_id=investor_id)
        serializer = InvestorSerializer(investor)
        return Response(serializer.data, status=200)

    def patch(self, request, user_id, investor_id):
        investor = get_object_or_404(Investor, user=user_id, investor_id=investor_id)
        serializer = InvestorSerializer(investor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, user_id, investor_id):
        investor = get_object_or_404(Investor, user=user_id, investor_id=investor_id)
        investor.delete()
        return Response(status=204)
