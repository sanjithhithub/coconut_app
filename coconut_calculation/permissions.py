from rest_framework.permissions import BasePermission

class IsVerifiedUser(BasePermission):
    """
    Custom permission to only allow verified users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'is_verified', False))
