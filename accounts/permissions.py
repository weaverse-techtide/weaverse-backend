from rest_framework import permissions


class IsAuthenticatedAndActive(permissions.IsAuthenticated):
    """
    권한 값으로 True/False를 반환합니다.
    - 사용자 객체 생성 및 인증 여부를 확인하고
      active한 인증자에게만 허용합니다.
    """

    message = "이 작업을 수행할 권한이 없습니다."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_active


class IsTutor(IsAuthenticatedAndActive):
    """
    권한 값으로 True/False를 반환합니다.
    - 요청 유형과 관계없이 강사(Tutor)이면 권한을 허용합니다.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff


class IsSuperUser(IsAuthenticatedAndActive):
    """
    권한 값으로 True/False를 반환합니다.
    - 요청 유형과 관계없이 관리자(superuser)이면 권한을 허용합니다.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser
