from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Deletion and modification
    only by the author of the post or the administrator.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_superuser)
