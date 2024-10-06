from django.db import transaction
from django.db.utils import DatabaseError
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, mixins, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import CustomUser
from .permissions import IsAuthenticatedAndActive, IsSuperUser, IsTutor
from .serializers import (
    CustomUserDetailSerializer,
    PasswordResetSerializer,
    StudentListSerializer,
    TutorListSerializer,
    UserRegistrationSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    """
    API의 페이지네이션을 정의합니다.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserRegisterationView(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    회원가입을 위한 뷰입니다.
    - POST: 학생 생성
    - 회원가입 또는 유효성 검사에 실패했을 때 에러메시지를 출력합니다.
    """

    queryset = CustomUser.objects.all()

    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                user = self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    {
                        "message": "성공적으로 회원가입 되었습니다.",
                        "user_id": user.id,
                    },
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
            except Exception as e:
                return Response(
                    {
                        "message": "회원가입에 실패했습니다. 다시 시도해주세요.",
                        "error": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "message": "실패했습니다. 다시 시도해주세요.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer):
        user = CustomUser.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            nickname=serializer.validated_data["nickname"],
        )
        return user


class PasswordResetView(generics.GenericAPIView):
    """
    비밀번호를 재설정합니다.
    - POST: 비밀번호 재설정
    """

    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"detail": "비밀번호가 성공적으로 변경되었습니다."},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {
                        "error": "비밀번호 재설정 중 오류가 발생했습니다. 다시 시도해 주세요."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    학생 유저를 목록 조회합니다.
    - 인증된 사용자만이 접근가능합니다.
    - GET: 학생 목록 조회
    """

    queryset = CustomUser.objects.filter(is_staff=False, is_active=True)
    serializer_class = StudentListSerializer
    permission_classes = [IsAuthenticatedAndActive]
    pagination_class = StandardResultsSetPagination

    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "email",
        "nickname",
        "created_at",
    ]  #  클라이언트가 정렬에 사용할 수 있는 필드들을 지정
    ordering = ["-created_at"]  # 기본 정렬 순서

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except PermissionDenied:
            return Response(
                {"error": "이 목록을 조회할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except DatabaseError:
            return Response(
                {
                    "error": "데이터베이스 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"학생 목록 조회 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StudentRetrieveUpdateDestroyView(
    generics.mixins.RetrieveModelMixin,
    generics.mixins.UpdateModelMixin,
    generics.mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """
    학생이 학생 정보를 조회, 수정, 삭제합니다.
    - GET: 학생 상세 조회
    - PUT: 학생 정보 수정
    - DELETE: 학생 삭제(소프트 삭제)
    """

    queryset = CustomUser.objects.filter(is_staff=False, is_active=True)
    serializer_class = CustomUserDetailSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        if self.request.user.pk != obj.pk:
            raise PermissionDenied("해당 사용자의 정보에 접근할 권한이 없습니다.")
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": f"조회 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, *args, **kwargs):
        return self._update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self._update(request, *args, partial=True, **kwargs)

    def _update(self, request, *args, partial=False, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"수정 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def perform_update(self, serializer):
        serializer.save()

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.is_active = False
            user.save()
            return Response(
                {"message": "계정이 비활성화되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": f"삭제 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TutorListView(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    """
    관리자가 강사 목록을 조회합니다.
    - GET: 강사 목록 조회
    """

    queryset = CustomUser.objects.filter(is_staff=True, is_active=True)
    serializer_class = TutorListSerializer
    permission_classes = [IsSuperUser]
    pagination_class = StandardResultsSetPagination

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["email", "nickname", "created_at"]
    ordering = ["-created_at"]  # 기본 정렬 순서

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except PermissionDenied:
            return Response(
                {"error": "이 목록을 조회할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except DatabaseError:
            return Response(
                {
                    "error": "데이터베이스 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"강사 목록 조회 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TutorRetrieveUpdateDestroyView(
    generics.mixins.RetrieveModelMixin,
    generics.mixins.UpdateModelMixin,
    generics.mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """
    관리자나 강사가 강사 정보를 조회, 수정, 삭제합니다.
    - GET: 강사 상세 조회
    - PUT: 강사 정보 수정
    - DELETE: 강사 삭제 (소프트 삭제)
    """

    queryset = CustomUser.objects.filter(is_staff=True, is_active=True)
    serializer_class = CustomUserDetailSerializer
    permission_classes = [IsTutor | IsSuperUser]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": f"조회 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, *args, **kwargs):
        return self._update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self._update(request, *args, partial=True, **kwargs)

    def _update(self, request, *args, partial=False, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"수정 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            tutor = self.get_object()
            tutor.is_active = False
            tutor.save()
            return Response(
                {"message": "강사 계정이 비활성화되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": f"삭제 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def check_object_permissions(self, request, obj):
        if not request.user.is_superuser and request.user.pk != obj.pk:
            raise PermissionDenied("해당 강사의 정보에 접근할 권한이 없습니다.")
        super().check_object_permissions(request, obj)
