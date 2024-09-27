from rest_framework.permissions import BasePermission


class IsStaffOrReadOnly(BasePermission):
    """
    사용자가 staff인 경우만 모든 권한을 가지고
    그렇지 않은 경우에는 안전한 요청(GET, HEAD, OPTIONS)인 경우에만 허용합니다.
    """

    def has_permission(self, request, view):
        """
        궈한 요청이 허용되는지 여부를 반환합니다.
        """

        return request.method in ["GET", "HEAD", "OPTIONS"] or request.user.is_staff
