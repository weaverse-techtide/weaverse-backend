from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 목록 조회나 생성 등의 작업에 대한 권한 검사
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 객체에 대한 권한 검사
        return obj.user == request.user
