import io

import boto3
import ffmpeg
from botocore.exceptions import ClientError
from django.conf import settings
from django.shortcuts import get_object_or_404
from PIL import Image as PILImage
from PIL import ImageFilter
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image, Video, VideoEventData
from .serializers import (ImageSerializer, UserViewEventListSerializer,
                          VideoEventSerializer, VideoSerializer)


# 리팩토링할 때 중복 함수 이곳에 작성
def optimize_image(self, image_file):
    """
    이미지를 최적화하는 메서드입니다.
    - 포맷 변환
    - 리사이징
    - 필터링
    """
    # Pillow를 사용하여 이미지 열기
    img = PILImage.open(image_file)

    # 포맷 변환
    img = img.convert("RGB")

    # 리사이징
    img.thumbnail((800, 600))

    # 이미지 필터링: 샤프닝 필터 적용
    img = img.filter(ImageFilter.SHARPEN)

    return img


class ImageCreateView(generics.CreateAPIView):
    # POST 요청: Image 객체를 사용해서 S3에 이미지 파일을 업로드합니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = request.FILES.get("image_url")

        if not image_file:
            return Response(
                {"error": "이미지 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        optimized_image = self.optimize_image(image_file)

        try:
            # 최적화된 이미지를 임시로 메모리에 저장
            image_io = io.BytesIO()
            optimized_image.save(image_io, format="JPEG", quality=85)
            image_io.seek(0)

            # S3에 파일 업로드
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))
            course = get_object_or_404(Course, id=request.data.get("course_id"))

            # 파일 이름 생성: 사용자 ID와 코스 ID를 포함
            if user:
                file_name = f"images/user_{user.id}/{image_file.name}"
            elif course:
                file_name = f"images/course_{course.id}/{image_file.name}"
            else:
                return Response(
                    {"error": "유효한 사용자 또는 코스가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            s3_client.upload_fileobj(
                image_io,
                settings.AWS_STORAGE_BUCKET_NAME,
                file_name,
                ExtraArgs={"ContentType": "image/jpeg"},
            )

            # 업로드된 파일의 URL 생성
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            # 시리얼라이저에 전달 후 저장
            serializer.validated_data["image_url"] = file_url
            image = serializer.save(file=file_url)

            return Response(
                self.get_serializer(image).data, status=status.HTTP_201_CREATED
            )
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImageListCreateView(generics.ListCreateAPIView):
    # GET 요청: 이미지 파일 목록을 가져옵니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save(course_id=self.request.data.get("course_id"))


class ImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # GET 요청: 특정 이미지 파일을 조회합니다.
    # PUT 요청: 특정 이미지 파일을 변경합니다.
    # DELETE 요청: 특정 이미지 파일을 삭제합니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = []

    def check_object_permissions(self, request, obj):
        if not request.user.is_staff and obj.course.tutor != request.user:
            raise PermissionDenied("접근 권한이 없습니다.")
        return super().check_object_permissions(request, obj)


class VideoCreateView(generics.CreateAPIView):
    # POST 요청: 영상 파일을 업로드합니다.

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES.get("file")
            if not file:
                return Response(
                    {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            max_image_size = 5 * 1024 * 1024  # 5MB

            if value.size > max_image_size:
                raise serializers.ValidationError(
                    "파일 크기는 5MB를 초과할 수 없습니다."
                )

            # S3 클라이언트 설정
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            try:
                # S3에 파일 업로드
                file_name = f"videos/{file.name}"
                s3_client.upload_fileobj(
                    file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_name,
                    ExtraArgs={"ContentType": file.content_type},
                )

                # 업로드된 파일의 URL 생성
                file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

                # 비디오 객체 생성 및 저장
                video = serializer.save(file=file_url)

                return Response(
                    self.get_serializer(video).data, status=status.HTTP_201_CREATED
                )
            except ClientError as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoListCreateView(generics.ListCreateAPIView):
    # GET 요청: 영상 파일 목록을 조회합니다.

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save(topic_id=self.request.data.get("topic_id"))


class VideoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # GET 요청: 특정 영상 파일을 조회합니다.
    # PUT 요청: 특정 영상 파일을 변경합니다.
    # DELETE 요청: 특정 영상 파일을 삭제합니다.

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = []

    def check_object_permissions(self, request, obj):
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if not request.user.is_staff and obj.topic.course.tutor != request.user:
                raise PermissionDenied("접근 권한이 없습니다.")
        return super().check_object_permissions(request, obj)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class VideoEventCreateView(generics.CreateAPIView):
    """
    POST 요청을 받아 영상 파일에 대한 이벤트 정보를 저장합니다.
    """

    queryset = VideoEventData.objects.all()
    serializer_class = VideoEventSerializer


class UserVideoEventListView(generics.ListAPIView):
    serializer_class = UserViewEventListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        video_id = self.kwargs.get("video_id")

        # 특정 사용자와 특정 비디오에 대한 이벤트 데이터를 필터링
        return VideoEventData.objects.filter(user_id=user_id, video_id=video_id)
