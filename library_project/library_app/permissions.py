from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает полный доступ только администраторам, остальные могут только читать."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешает доступ к объектам только их владельцу или администратору"""

    def has_object_permission(self, request, view, obj):
        return request.user and (obj.user == request.user or request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Позволяет владельцу объекта изменять его, остальные — только читать.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
