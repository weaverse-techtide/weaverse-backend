from django.shortcuts import get_object_or_404
from jwtauth.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .permissions import (
    IsAuthenticatedOrCreateOnly,
    IsSuperUser,
    IsTutor,
    IsTutorOrSuperUserOrSuperUserCreateOnly,
)
from .serializers import CustomUserSerializer, PasswordResetSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """
    API의 페이지네이션을 정의합니다.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PasswordResetView(generics.GenericAPIView):
    """
    비밀번호를 재설정합니다.
    POST: 비밀번호 재설정 (PUT이 아닌)
    """

    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK,
        )


class StudentListCreateView(
    generics.GenericAPIView,
    generics.mixins.ListModelMixin,
    generics.mixins.CreateModelMixin,
):
    """
    학생 유저를 목록 조회 및 생성합니다.
    - GET: 학생 목록 조회
    - POST: 학생 생성
    """

    queryset = CustomUser.objects.filter(is_staff=False, is_active=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrCreateOnly]  # 자동 403 Forbidden
    pagination_class = StandardResultsSetPagination
    authentication_classes = JWTAuthentication  # 자동 401 Unauthorized

    ordering_fields = ["email", "first_name", "last_name", "date_joined"]
    ordering = ["-date_joined"]  # 기본 정렬 순서

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_staff=False, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentRetrieveUpdateDestroyView(
    generics.GenericAPIView,
    generics.mixins.RetrieveModelMixin,
    generics.mixins.UpdateModelMixin,
    generics.mixins.DestroyModelMixin,
):
    """
    학생 유저에 대해 조회, 수정, 삭제합니다.
    GET: 학생 상세 조회
    PUT: 학생 정보 수정
    DELETE: 학생 소프트 삭제
    """

    queryset = CustomUser.objects.filter(is_staff=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = JWTAuthentication

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        if self.request.user.pk != obj.pk:
            raise PermissionDenied("해당 사용자는 권한이 없는 접근입니다.")
        return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TutorListCreateView(
    generics.GenericAPIView,
    generics.mixins.ListModelMixin,
    generics.mixins.CreateModelMixin,
):
    """
    관리자 사용자 목록 조회 및 생성합니다.
    GET: 관리자 목록 조회
    POST: 관리자 생성
    """

    queryset = CustomUser.objects.filter(is_staff=True, is_active=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsTutorOrSuperUserOrSuperUserCreateOnly]
    pagination_class = StandardResultsSetPagination
    authentication_classes = JWTAuthentication

    ordering_fields = ["email", "first_name", "last_name", "date_joined"]
    ordering = ["-date_joined"]  # 기본 정렬 순서

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_staff=True, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TutorRetrieveUpdateDestroyView(
    generics.GenericAPIView,
    generics.mixins.RetrieveModelMixin,
    generics.mixins.UpdateModelMixin,
    generics.mixins.DestroyModelMixin,
):
    """
    관리자 사용자 조회, 수정, 삭제합니다.
    GET: 관리자 상세 조회
    PUT: 관리자 정보 수정
    DELETE: 관리자 소프트 삭제
    """

    queryset = CustomUser.objects.filter(is_staff=True)
    serializer_class = CustomUserSerializer
    permission_classes = [IsTutor | IsSuperUser]
    authentication_classes = JWTAuthentication

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        tutor = self.get_object()
        tutor.is_active = False
        tutor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TutorStudentView(generics.ListAPIView):
    """
    특정 튜터의 학생 목록을 조회합니다.
    GET: 튜터의 학생 목록 조회
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated & (IsTutor | IsSuperUser)]
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination
    filter_backends = [OrderingFilter]

    ordering_fields = ["email", "first_name", "last_name", "created_at"]
    ordering = ["created_at"]  # 기본 정렬 순서

    def get_queryset(self):
        tutor_id = self.kwargs.get("tutor_id")
        try:
            tutor = CustomUser.objects.get(id=tutor_id, is_staff=True)
        except CustomUser.DoesNotExist:
            raise NotFound("해당 튜터를 찾을 수 없습니다.")

        if self.request.user.id != tutor_id and not self.request.user.is_superuser:
            raise PermissionDenied("이 정보에 접근할 권한이 없습니다.")

        return tutor.students.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "tutor_id": self.kwargs.get("tutor_id"),
                "student_count": queryset.count(),
                "students": serializer.data,
            }
        )
