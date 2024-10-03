from rest_framework import permissions


class BaseAuthPermission(permissions.IsAuthenticated):
    """
    권한 값으로 True/False를 반환합니다.
    - 사용자 객체 생성 및 인증 여부를 확인하고 인증자에게만 허용합니다.
    """

    message = "이 작업을 수행할 권한이 없습니다."


class IsAuthenticatedOrCreateOnly(BaseAuthPermission):
    """
    권한 값으로 True/False를 반환합니다.
    - GET 요청을 인증된 사용자에게 허용합니다.
    - POST 요청을 누구에게나 허용합니다.
    """

    message = "이 작업을 수행하려면 로그인이 필요합니다."

    def has_permission(self, request, view):
        if request.method == "GET":
            return super().has_permission(request, view)
        elif request.method == "POST":
            return True
        return False


class IsTutor(BaseAuthPermission):
    """
    권한 값으로 True/False를 반환합니다.
    - 요청 유형과 관계없이 강사(Tutor)이면 권한을 허용합니다.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff


class IsSuperUser(BaseAuthPermission):
    """
    권한 값으로 True/False를 반환합니다.
    - 요청 유형과 관계없이 관리자(superuser)이면 권한을 허용합니다.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser


class IsTutorOrSuperUserOrSuperUserCreateOnly(BaseAuthPermission):
    """
    권한 값으로 True/False를 반환합니다.
    - GET 요청을 강사(tutor) 또는 관리자(superuser)에게 허용합니다.
    - POST 요청을 관리자(superuser)에게만 허용합니다.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.method == "GET":
            return request.user.is_staff or request.user.is_superuser
        elif request.method == "POST":
            return request.user.is_superuser
        return False
