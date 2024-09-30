from rest_framework import permissions


class BaseAuthPermission(permissions.IsAuthenticated):
    message = "이 작업을 수행할 권한이 없습니다."


class IsAuthenticatedOrCreateOnly(BaseAuthPermission):
    """
    GET 요청에 대해서는 인증을 요구하고, POST 요청은 누구나 권한을 허용합니다.
    """

    message = "이 작업을 수행하려면 로그인이 필요합니다."

    def has_permission(self, request, view):
        if request.method == "GET":
            return super().has_permission(request, view)
        elif request.method == "POST":
            return True
        return False


class IsAuthenticatedAndTutor(BaseAuthPermission):
    """
    인증된, 그리고 유저 중 관리자(tutor) 권한을 가진 사용자에게만 접근을 허용합니다.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff


class IsAuthenticatedAndSuperUser(BaseAuthPermission):
    """
    인증된, 그리고 유저 중 수퍼유저(superuser) 권한을 가진 사용자에게만 접근을 허용합니다.
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser


class IsTutorOrSuperUserOrSuperUserCreateOnly(BaseAuthPermission):
    """
    GET 요청에 대해서는 인증된, 그리고 유저 중 강사(tutor)와 수퍼 유저(superuser)를,
    POST 요청에 대해서는 인증된, 그리고 유저 중 수퍼 유저에게 권한을 허용합니다.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.method == "GET":
            return request.user.is_staff or request.user.is_superuser
        elif request.method == "POST":
            return request.user.is_superuser
        return False
