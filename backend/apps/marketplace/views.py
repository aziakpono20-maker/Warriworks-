from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ArtisanProfile, ServiceCategory
from .serializers import (
    ArtisanSerializer, ArtisanProfileUpdateSerializer, CategorySerializer,
)


class ArtisanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArtisanSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['display_name', 'skill', 'location']
    filterset_fields = ['skill', 'location', 'verified']
    ordering_fields = ['display_name', 'created_at']

    def get_queryset(self):
        return ArtisanProfile.objects.filter(
            verified=True, is_available=True
        ).select_related('user')


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class MyArtisanProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, user):
        if getattr(user, 'role', None) != 'artisan':
            raise PermissionDenied('Only artisan accounts can manage an artisan profile.')
        try:
            return user.artisan_profile
        except ArtisanProfile.DoesNotExist:
            raise ValidationError('Your artisan profile has not been created. Contact support.')

    def get(self, request):
        profile = self.get_profile(request.user)
        return Response(ArtisanSerializer(profile, context={'request': request}).data)

    def patch(self, request):
        profile = self.get_profile(request.user)
        serializer = ArtisanProfileUpdateSerializer(
            profile, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArtisanSerializer(profile, context={'request': request}).data)
