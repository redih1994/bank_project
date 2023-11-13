from rest_framework import permissions

class IsBankerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated before accessing attributes
        if request.user.is_authenticated:
            return request.user.is_banker
        return False
