from rest_framework.permissions import BasePermission


class UserIsAuthorized(BasePermission):

    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        return obj.is_staff or request.user == obj


class ForbiddenAction(BasePermission):

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False