
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


@method_decorator(csrf_protect, name='dispatch')
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    # The legacy registration endpoint creates customers only.
    registration_role = User.Role.CUSTOMER

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save(role=self.registration_role)

        login(request, user)

        return Response(UserSerializer(user).data, status=201)


class ArtisanRegisterView(RegisterView):
    # This role is determined by Django, not the browser.
    registration_role = User.Role.ARTISAN


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        login(request, user)

        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=204)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)