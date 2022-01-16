from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    # has_permission and has_object_permission
    # we use has_object_permission -> так действие делаем над объектом
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.user

