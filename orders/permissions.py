from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Доступ только для пользователей с ролью 'owner'."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return profile is not None and profile.role == 'owner'


class IsOwnerOrMasterReadOnly(permissions.BasePermission):
    """Владелец - полный доступ. Мастер - только чтение."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        if profile is None:
            return False
        if profile.role == 'owner':
            return True
        return request.method in permissions.SAFE_METHODS