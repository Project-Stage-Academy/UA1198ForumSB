from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from investors.models import Investor
from investors.serializers import InvestorSerializer

from startups.models import Startup
from startups.serializers import StartupSerializer

from projects.models import Project
from projects.serializers import ProjectSerializer

from users.models import CustomUser
from users.serializers import NamespaceSerializer
from users.permissions import *

class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'
    

class NamespaceSelectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token: str = request.COOKIES.get('refresh')
        
        if not refresh_token:
            return Response({"error": "Authentication credentials were not provided."}, 
                            status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            old_refresh_token = RefreshToken(refresh_token)
        except TokenError:
            return Response({"error": "Invalid or expired token."},
                            status=status.HTTP_401_UNAUTHORIZED)
             
        user_id = old_refresh_token.payload.get('user_id')
        user = get_object_or_404(CustomUser, user_id=user_id)

        serializer = NamespaceSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            namespace_id: int = serializer.validated_data['name_space_id']
            namespace_name: str = serializer.validated_data['name_space_name']

            old_refresh_token.blacklist()
            new_refresh_token = RefreshToken.for_user(user)
            new_refresh_token.payload.update({
                'name_space_id': namespace_id,
                'name_space_name': namespace_name
            })

            response = Response("Namespace has been successfully updated.", 
                                status=status.HTTP_200_OK)
            response.set_cookie(
                'refresh',
                new_refresh_token,
                httponly=True,
                secure=True,
                samesite='Strict',
            )
            response.set_cookie(
                'access',
                new_refresh_token.access_token,
                httponly=True,
                secure=True,
                samesite='Strict',
            )
            return response
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserStartupListView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected
    ]

    def get(self, request, user_id):
        startups = get_list_or_404(Startup, user=user_id)
        serializer = StartupSerializer(startups, many=True)
        return Response(serializer.data, status=200)
    
    def post(self, request, user_id):
        serializer = StartupSerializer(data={**request.data, 'user': user_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserStartupDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected,
        ThisStartup
    ]

    def get(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        serializer = StartupSerializer(startup)
        return Response(serializer.data, status=200)
    
    def patch(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        serializer = StartupSerializer(startup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, user_id, startup_id):
        # if the startup has some investors subscriptions we can't delete it
        # add appropriate permission
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        startup.delete()
        return Response(status=204)


class UserStartupProjectView(APIView):
    permission_classes = [
        IsAuthenticated,
        ThisUserPermission,
        IsStartupNamespaceSelected,
        ThisStartup
    ]

    def get(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        serializer = StartupSerializer(project)
        return Response(serializer.data, status=200)

    def post(self, request, user_id, startup_id):
        serializer = StartupSerializer(data={
            **request.data,
            'user': user_id,
            'startup': startup_id
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, user_id, startup_id):
        startup = get_object_or_404(Startup, user=user_id, startup_id=startup_id)
        project = get_object_or_404(Project, startup=startup)
        project.delete()
        return Response(status=204)


class UserInvestorListView(APIView):
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

class UserInvestorDetailView(APIView):
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
