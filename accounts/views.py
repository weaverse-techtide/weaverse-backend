from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .permissions import (
    IsAuthenticatedAndSuperUser,
    IsAuthenticatedAndTutor,
    IsAuthenticatedOrCreateOnly,
    IsTutorOrSuperUserOrSuperUserCreateOnly,
)
from .serializers import CustomUserSerializer


def paginate_queryset(request, queryset):
    """
    쿼리셋을 받아 페이지네이션을 적용합니다.
    """
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(queryset, request)
    return (paginator, result_page)


@api_view(["GET", "POST"])
@permission_classes(  # 권한이 거부될 경우 자동으로 적절한 응답(403 Forbidden)을 반환
    [IsAuthenticatedOrCreateOnly]
)
def student_list_create(request):
    """
    학생 유저를 목록 조회 및 생성합니다.
    """
    if request.method == "GET":
        users = CustomUser.objects.filter(is_staff=False, is_active=True)
        paginator, result_page = paginate_queryset(request, users)
        serializer = CustomUserSerializer(result_page, many=True)
        return paginator.get_paginated_response(  # 페이지네이션된 결과를 정보와 반환 (총 항목 수, 다음/이전 페이지 링크)
            serializer.data
        )
    elif request.method == "POST":
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_staff=False, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def student_retrieve_update_delete(request, pk):
    """
    학생 유저에 대해 조회, 수정, 삭제합니다.
    """
    user = get_object_or_404(CustomUser, pk=pk, is_staff=False)

    if request.user.pk != user.pk:  # 객체 수준 권한 검사
        raise PermissionDenied(  # 다른 사용자의 정보에 접근하려고 하면 403 Forbidden 응답 반환
            "해당 사용자는 권한이 없는 접근입니다."
        )

    if request.method == "GET":
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        user.is_active = False  # 소프트 삭제로 데이터 보존
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticatedAndTutor, IsAuthenticatedAndSuperUser])
def student_count(request):
    """
    활동 중인 학생 사용자 수 조회합니다.
    """
    count = CustomUser.objects.filter(is_staff=False, is_active=True).count()
    return Response({"count": count})  # 학생 수 조회에 대한 응답 구조


@api_view(["GET", "POST"])
@permission_classes([IsTutorOrSuperUserOrSuperUserCreateOnly])
def tutor_list_create(request):
    """
    관리자 사용자 목록 조회 및 생성합니다.
    """
    if request.method == "GET":
        tutors = CustomUser.objects.filter(is_staff=True, is_active=True)
        paginator, result_page = paginate_queryset(request, tutors)
        serializer = CustomUserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == "POST":
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_staff=True, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedAndTutor, IsAuthenticatedAndSuperUser])
def tutor_retrieve_update_delete(request, pk):
    """
    관리자 사용자 조회, 수정, 삭제합니다.
    """
    tutor = get_object_or_404(CustomUser, pk=pk, is_staff=True)

    if request.method == "GET":
        serializer = CustomUserSerializer(tutor)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CustomUserSerializer(tutor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        tutor.is_active = False
        tutor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
