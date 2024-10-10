import io

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.shortcuts import get_object_or_404
from PIL import Image as PILImage
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image, Video, VideoEventData
from .serializers import (
    ImageSerializer,
    VideoEventSerializer,
    VideoSerializer,
    WatchHistorySerializer,
)

# 리팩토링할 때 중복 함수 이곳에 작성


class ImageCreateView(generics.CreateAPIView):
    # POST 요청: 이미지 파일을 업로드합니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # 시리얼라이저에서 유효성 검사 수행
        if serializer.is_valid():
            file = request.FILES.get("file")
            if not file:
                return Response(
                    {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            try:
                # 이미지 최적화 (선택사항)
                img = PILImage.open(file)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                buffer.seek(0)

                # S3에 파일 업로드
                file_name = f"images/{file.name}"
                s3_client.upload_fileobj(
                    buffer,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_name,
                    ExtraArgs={"ContentType": "image/jpeg"},
                )

                # 업로드된 파일의 URL 생성
                file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

                # 이미지 객체 생성 및 저장
                image = serializer.save(file=file_url)

                return Response(
                    self.get_serializer(image).data, status=status.HTTP_201_CREATED
                )
            except ClientError as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class VideoEventListView(APIView):
    # GET 요청:
    def get(self, request, video_id):
        # video_id는 URL에서 가져옵니다
        video = get_object_or_404(Video, id=video_id)
        video_event_data_list = (
            video.videoEventData.all()
        )  # related_name을 통해 데이터 조회
        return Response({"events": [str(event) for event in video_event_data_list]})


class WatchHistoryRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    # GET 요청: 특정 영상의 시청 기록을 조회합니다.
    # PUT 요청: 특정 영상의 시청 기록을 업데이트합니다.

    serializer_class = WatchHistorySerializer
    permission_classes = []

    def get_object(self):
        pass

    def perform_update(self, serializer):
        pass
