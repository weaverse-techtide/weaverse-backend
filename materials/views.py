import io

import boto3
import ffmpeg
from accounts.permissions import IsSuperUser, IsTutor
from botocore.exceptions import ClientError
from django.conf import settings
from django.shortcuts import get_object_or_404
from PIL import Image as PILImage
from PIL import ImageFilter
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Image, Video, VideoEventData
from .serializers import (ImageSerializer, UserViewEventListSerializer,
                          VideoEventSerializer, VideoSerializer)


# 리팩토링할 때 중복 함수 이곳에 작성
def optimize_image(image_file):
    """
    이미지를 최적화하는 메서드입니다.
    - 포맷 변환
    - 리사이징
    - 필터링
    """

    img = PILImage.open(image_file)
    img = img.convert("RGB")
    img.thumbnail((800, 600))
    img = img.filter(ImageFilter.SHARPEN)

    return img


def optimize_video(self, video_file):
    """
    비디오 파일을 최적화합니다.
    - 포맷 변환
    - 리사이징 작업
    """
    # 최적화된 비디오를 임시 메모리에 저장
    output_io = io.BytesIO()

    ffmpeg.input(video_file).output(
        output_io, format="mp4", video_bitrate="1000k", s="640x360", preset="fast"
    ).run(overwrite_output=True)

    # 임시 메모리의 포인터를 처음으로 이동
    output_io.seek(0)
    return output_io


def upload_to_s3(image_io, file_name):
    """
    S3에 파일을 업로드하는 함수입니다.
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    s3_client.upload_fileobj(
        image_io,
        settings.AWS_STORAGE_BUCKET_NAME,
        file_name,
        ExtraArgs={"ContentType": "image/jpeg"},
    )


class ImageCreateView(generics.CreateAPIView):
    # POST 요청: Image 객체를 사용해서 S3에 이미지 파일을 업로드합니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = request.FILES.get("file")

        if not image_file:
            return Response(
                {"error": "이미지 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        optimized_image = optimize_image(image_file)

        try:
            # 최적화된 이미지를 임시로 메모리에 저장
            image_io = io.BytesIO()
            optimized_image.save(image_io, format="JPEG", quality=85)
            image_io.seek(0)

            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))

            # 파일 이름 생성: 사용자 ID와 코스 ID를 포함
            if user:
                timestamp = int(time.time())
                file_name = f"images/user_{user.id}/{timestamp}_{image_file.name}"
            else:
                return Response(
                    {"error": "유효한 사용자가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # S3에 파일 업로드
            upload_to_s3(image_io, file_name)

            # 업로드된 파일의 URL 생성
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            image = serializer.save(image_url=file_url)

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
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(course_id=self.request.data.get("course_id"))


class ImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # GET 요청: 특정 이미지 파일을 조회합니다.
    # PUT 요청: 특정 이미지 파일을 변경합니다.
    # DELETE 요청: 특정 이미지 파일을 삭제합니다.

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if not request.user.is_staff and obj.course.tutor != request.user:
            raise PermissionDenied("접근 권한이 없습니다.")
        return super().check_object_permissions(request, obj)

    def get(self, request, *args, **kwargs):
        image = self.get_object()  # 특정 이미지 객체 가져오기

        # S3에서 이미지 다운로드
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            # S3에서 객체 가져오기
            s3_response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=image.image_url.split("/")[-1],
            )

            # 파일을 바이너리 형식으로 반환
            response = HttpResponse(
                s3_response["Body"].read(),
                content_type="image/jpeg",
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{image.image_url.split("/")[-1]}"'
            )
            return response

        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        image = self.get_object()  # 특정 이미지 객체 가져오기
        serializer = self.get_serializer(image, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 이미지 파일을 최적화하고 S3에 업로드
        image_file = request.FILES.get("image_url")
        if image_file:
            optimized_image = self.optimize_image(image_file)

            # 최적화된 이미지를 임시로 메모리에 저장
            image_io = io.BytesIO()
            optimized_image.save(image_io, format="JPEG", quality=85)
            image_io.seek(0)

            # 기존 이미지 삭제 (S3에서)
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=image.image_url.split("/")[-1],
            )

            # 새로운 파일 이름 생성
            timestamp = int(time.time())
            file_name = f"images/user_{image.user.id}/{timestamp}_{image_file.name}"

            # S3에 새로운 이미지 업로드
            upload_to_s3(image_io, file_name, content_type="image/jpeg")

            # 업로드된 파일의 URL 생성
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            image = serializer.save(image_url=file_url)

        return Response(self.get_serializer(image).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        image = self.get_object()  # 특정 이미지 객체 가져오기

        # S3에서 이미지 삭제
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=image.image_url.split("/")[-1],
            )
            # 데이터베이스에서 이미지 객체 삭제
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoCreateView(generics.CreateAPIView):
    # POST 요청: 영상 파일을 업로드합니다.

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsTutor | IsSuperUser]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video_file = request.FILES.get("video_url")
        if not video_file:
            return Response(
                {"error": "비디오 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        optimized_video = self.optimize_video(video_file)

        try:
            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))

            # 파일 이름 생성
            if user:
                timestamp = int(time.time())
                file_name = f"video/user_{user.id}/{timestamp}_{video_file.name}"

            # S3에 파일 업로드
            upload_to_s3(optimized_video, file_name)

            # 업로드된 파일의 URL 생성
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            # 비디오 객체 생성 및 저장
            serializer.validated_data["video_url"] = file_url
            video = serializer.save(video_url=file_url)

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
    permission_classes = [IsTutor | IsSuperUser]

    def perform_create(self, serializer):
        serializer.save(topic_id=self.request.data.get("topic_id"))


class VideoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # GET 요청: 특정 영상 파일을 조회합니다.
    # PUT 요청: 특정 영상 파일을 변경합니다.
    # DELETE 요청: 특정 영상 파일을 삭제합니다.

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsSuperUser]

    def check_object_permissions(self, request, obj):
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if not request.user.is_staff and obj.topic.course.tutor != request.user:
                raise PermissionDenied("접근 권한이 없습니다.")
        return super().check_object_permissions(request, obj)

    def get(self, request, *args, **kwargs):
        video = self.get_object()  # 특정 비디오 객체 가져오기

        # S3에서 비디오 다운로드
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            # S3에서 비디오 객체 가져오기
            s3_response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=video.video_url.split("/")[-1],
            )

            # 파일을 바이너리 형식으로 반환
            response = HttpResponse(
                s3_response["Body"].read(),
                content_type="video/mp4",  # 비디오 형식에 따라 변경 가능
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{video.video_url.split("/")[-1]}"'
            )
            return response

        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        video = self.get_object()  # 특정 비디오 객체 가져오기
        serializer = self.get_serializer(video, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 비디오 파일을 최적화하고 S3에 업로드
        video_file = request.FILES.get("video_url")
        if video_file:
            optimized_video = self.optimize_video(video_file)

            # S3에서 기존 비디오 삭제
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=video.video_url.split("/")[-1],
            )

            # 새로운 파일 이름 생성
            timestamp = int(time.time())
            file_name = f"video/user_{video.user.id}/{timestamp}_{video_file.name}"

            # S3에 새로운 비디오 업로드
            upload_to_s3(optimized_video, file_name)

            # 업로드된 파일의 URL 생성
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            # 시리얼라이저에 전달 후 저장
            serializer.validated_data["video_url"] = file_url
            video = serializer.save()

        return Response(self.get_serializer(video).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        video = self.get_object()  # 특정 비디오 객체 가져오기

        # S3에서 비디오 삭제
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=video.video_url.split("/")[-1],
            )
            # 데이터베이스에서 비디오 객체 삭제
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
