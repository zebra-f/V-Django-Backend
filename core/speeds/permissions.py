from rest_framework.permissions import BasePermission


class UserIsAuthorized(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        
        return request.user.is_staff or request.user == obj.user


class ForbiddenAction(BasePermission):

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False
    

class SpeedFeedbackPermissions(UserIsAuthorized):
    
    def has_object_permission(self, request, view, obj):
        has_object_permission = super().has_object_permission(request, view, obj)
        
        if request.user != obj.speed.user:
            if not obj.speed.is_public:
                return False
        
        return has_object_permission


class SpeedBookmarkPermissions(SpeedFeedbackPermissions):
    pass