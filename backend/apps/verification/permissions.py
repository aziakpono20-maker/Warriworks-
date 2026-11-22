from rest_framework.permissions import BasePermission

class IsArtisanOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'artisan')

class IsWarriWorksAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff or getattr(user, 'role', None) == 'admin'))
