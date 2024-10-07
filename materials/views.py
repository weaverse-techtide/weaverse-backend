import io

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import render
from PIL import Image as PILImage
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Image, Video
from .serializers import ImageSerializer, VideoSerializer, WatchHistorySerializer


class ImageCreateView(generics.CreateAPIView):
    # POST 요청: 이미지 파일을 업로드합니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
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

            # 이미지 파일 검증
            try:
                img = PILImage.open(file)
                img.verify()
            except:
                return Response(
                    {"error": "Invalid image file"}, status=status.HTTP_400_BAD_REQUEST
                )

            # S3 클라이언트 설정
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
    # GET 요청: 특정 영상 파일을 조회하고 스트리밍합니다.
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
        if request.query_params.get("stream", "").lower() == "true":
            return self.stream_video(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def stream_video(self, video):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        file_key = str(video.file)  # S3에 저장된 파일의 키

        def generate():
            offset = 0
            chunk_size = 8388608  # 8MB 청크 크기
            while True:
                try:
                    file_object = s3.get_object(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=file_key,
                        Range=f"bytes={offset}-{offset+chunk_size-1}",
                    )
                    data = file_object["Body"].read()
                    if not data:
                        break
                    yield data
                    offset += len(data)
                except Exception as e:
                    print(f"영상 스트림 실패: {str(e)}")
                    break

        response = StreamingHttpResponse(
            streaming_content=generate(), content_type="video/mp4"
        )
        response["Content-Disposition"] = f'inline; filename="{video.title}.mp4"'
        return response


class WatchHistoryRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    # PUT 요청: 특정 영상의 시청 기록을 업데이트합니다.
    # GET 요청: 특정 영상의 시청 기록을 조회합니다.

    serializer_class = WatchHistorySerializer
    permission_classes = []

    def get_object(self):
        pass

    def perform_update(self, serializer):
        pass
