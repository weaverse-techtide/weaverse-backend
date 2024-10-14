import io

import boto3
import ffmpeg
from accounts.models import CustomUser
from accounts.permissions import IsSuperUser, IsTutor
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from PIL import Image as PILImage
from PIL import ImageFilter
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Image, Video, VideoEventData
from .serializers import (ImageSerializer, UserViewEventListSerializer,
                          VideoEventDataSerializer, VideoSerializer)

User = get_user_model()


def optimize_image(image_file):
    """
    이미지 파일을 최적화합니다.
    - 포맷 변환
    - 리사이징
    - 필터링
    """

    img = PILImage.open(image_file)
    img = img.convert("RGB")
    img.thumbnail((800, 600))
    img = img.filter(ImageFilter.SHARPEN)

    optimized_io = io.BytesIO()
    img.save(optimized_io, format="JPEG", quality=85)
    optimized_io.seek(0)

    return optimized_io


def optimize_video(video_file):
    """
    동영상 파일을 최적화합니다.
    - 포맷 변환
    - 리사이징 작업
    """
    output_io = io.BytesIO()

    ffmpeg.input(video_file).output(
        output_io, format="mp4", video_bitrate="1000k", s="640x360", preset="fast"
    ).run(overwrite_output=True)

    output_io.seek(0)
    return output_io


def upload_to_s3(file_io, file_name, content_type):
    """
    파일을 S3에 업로드합니다.
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    s3_client.upload_fileobj(
        file_io,
        settings.AWS_STORAGE_BUCKET_NAME,
        file_name,
        ExtraArgs={"ContentType": content_type},
    )


class ImageCreateView(generics.CreateAPIView):
    """
    이미지 파일을 최적화한 후 S3에 업로드합니다.
    - 권한: 인증된 사용자만이 이미지 파일을 업로드할 수 있습니다.
    - 위치: S3에서 'images/사용자 식별자(user_id)' 폴더에 이미지 파일을 업로드합니다.
    - 사용자 편의성: 파일명 중복을 피하기 위해, 생성 시간을 포함시킵니다.
    - 에러: AWS S3에 대한 요청이 실패했을 때 발생했을 때 ClientError를 발생시킵니다.
    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
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

        optimized_image = optimize_image(image_file)

        try:

            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))

            if user:
                timestamp = int(time.time())
                file_name = f"images/user_{user.id}/{timestamp}_{image_file.name}"
            else:
                return Response(
                    {"error": "유효한 사용자가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            upload_to_s3(optimized_image, file_name, "image/jpeg")

            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            image = serializer.save(image_url=file_url)

            return Response(
                self.get_serializer(image).data, status=status.HTTP_201_CREATED
            )
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            del optimized_image


class ImageListView(generics.ListAPIView):
    """
    저장한 이미지 파일 목록을 가져옵니다.
    - 권한: 인증된 사용자만이 이미지 파일 목록을 조회할 수 있습니다.
    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    기존의 이미지 파일을 삭제 후 S3에 최적화 및 갱신하거나 소프트 삭제합니다.
    - 권한: 인증된 사용자만이 이미지 파일을 갱신할 수 있습니다.
    - 위치: S3에서 'images/사용자 식별자(user_id)' 폴더에 이미지 파일을 업로드합니다.
    - 사용자 편의성: 파일명 중복을 피하기 위해, 생성 시간을 포함시킵니다.
    - 에러: AWS S3에 대한 요청이 실패했을 때 발생했을 때 ClientError를 발생시킵니다.
    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        image = self.get_object()

        if image.user != request.user:
            return Response(
                {"error": "해당 이미지에 대한 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(image, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        image_file = request.FILES.get("image_url")

        if not image_file:
            return Response(
                {"error": "이미지 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

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

            optimized_image = self.optimize_image(image_file)

            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))

            if user:
                timestamp = int(time.time())
                file_name = f"images/user_{image.user.id}/{timestamp}_{image_file.name}"

            upload_to_s3(optimized_image, file_name, "image/jpeg")

            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            image = serializer.save(image_url=file_url)

            return Response(self.get_serializer(image).data, status=status.HTTP_200_OK)
        except ClientError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": "이미지를 처리하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            del optimized_image

    def delete(self, request, *args, **kwargs):
        image = self.get_object()

        if image.user != request.user:
            return Response(
                {"error": "해당 이미지에 대한 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            image.is_deleted = True
            image.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoCreateView(generics.CreateAPIView):
    """
    동영상 파일을 최적화한 후 S3에 업로드합니다.
    - 권한: 인증된 사용자 중 강사와 수퍼유저만이 동영상 파일을 업로드할 수 있습니다.
    - 위치: S3에서 'videos/사용자 식별자(user_id)' 폴더에 동영상 파일을 업로드합니다.
    - 사용자 편의성: 파일명 중복을 피하기 위해, 생성 시간을 포함시킵니다.
    - 에러: AWS S3에 대한 요청이 실패했을 때 발생했을 때 ClientError를 발생시킵니다.
    """

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
                {"error": "동영상 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        optimized_video = self.optimize_video(video_file)

        try:
            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))

            if user:
                timestamp = int(time.time())
                file_name = f"videos/user_{user.id}/{timestamp}_{video_file.name}"

            upload_to_s3(optimized_video, file_name, "video/mp4")

            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            serializer.validated_data["video_url"] = file_url
            video = serializer.save(video_url=file_url)

            return Response(
                self.get_serializer(video).data, status=status.HTTP_201_CREATED
            )
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            del optimized_video


class VideoListView(generics.ListAPIView):
    """
    저장한 이미지 파일 목록을 가져옵니다.
    - 권한: 인증된 사용자만이 이미지 파일 목록을 조회할 수 있습니다.
    """

    queryset = Video.objects.filter(is_deleted=False)
    serializer_class = VideoSerializer
    permission_classes = [IsTutor | IsSuperUser]


class VideoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    기존의 동영상 파일을 삭제 후 S3에 최적화 및 갱신하거나 소프트 삭제합니다.
    - 권한: 인증된 사용자 중 수퍼유저만이 이미지 파일을 갱신할 수 있습니다.
    - 위치: S3에서 'videos/사용자 식별자(user_id)' 폴더에 이미지 파일을 업로드합니다.
    - 사용자 편의성: 파일명 중복을 피하기 위해, 생성 시간을 포함시킵니다.
    - 에러: AWS S3에 대한 요청이 실패했을 때 발생했을 때 ClientError를 발생시킵니다.
    """

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsSuperUser]

    def check_object_permissions(self, request, obj):
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if not request.user.is_staff and obj.topic.course.tutor != request.user:
                raise PermissionDenied("접근 권한이 없습니다.")
        return super().check_object_permissions(request, obj)

    def put(self, request, *args, **kwargs):
        video = self.get_object()
        serializer = self.get_serializer(video, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        video_file = request.FILES.get("video_url")
        if not video_file:
            return Response(
                {"error": "동영상 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            optimized_video = self.optimize_video(video_file)

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

            user = get_object_or_404(CustomUser, id=request.data.get("user_id"))

            if user:
                timestamp = int(time.time())
                file_name = f"videos/user_{user.id}/{timestamp}_{video_file.name}"

            upload_to_s3(optimized_video, file_name, "video/mp4")

            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

            serializer.validated_data["video_url"] = file_url
            video = serializer.save()

            return Response(self.get_serializer(video).data, status=status.HTTP_200_OK)
        except ClientError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": "동영상을 처리하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            del optimized_video

    def delete(self, request, *args, **kwargs):
        video = self.get_object()

        if video.user != request.user:
            return Response(
                {"error": "해당 동영상에 대한 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            image.is_deleted = True
            image.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClientError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserVideoEventCreateView(generics.CreateAPIView):
    """
    특정 사용자에 대한 동영상 시청 이벤트를 생성합니다.
    - 권한: 인증된 사용자만이 동영상 시청 기록을 남길 수 있습니다.
    """

    queryset = VideoEventData.objects.all()
    serializer_class = VideoEventDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(CustomUser, id=user_id)

        video_id = self.request.data.get("video_id")
        video = get_object_or_404(Video, id=video_id)

        serializer.save(user=user, video=video)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        video_id = request.data.get("video_id")

        user = get_object_or_404(CustomUser, id=user_id)
        video = get_object_or_404(Video, id=video_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=user, video=video)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserVideoEventListView(generics.ListAPIView):
    """
    특정 사용자에 대한 동영상 시청 이벤트 기록을 가져옵니다.
    - 권한: 인증된 사용자 중 수퍼유저만이 동영상 시청 기록을 조회할 수 있습니다.
    """

    queryset = VideoEventData.objects.all()
    serializer_class = VideoEventDataSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        video_id = self.kwargs["video_id"]

        return VideoEventData.objects.filter(user__id=user_id, video__id=video_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            raise NotFound("해당 사용자의 비디오 시청 기록을 찾을 수 없습니다.")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserVideoEventRetrieveUpdateDestroyView(generics.ListAPIView):
    """
    특정 사용자에 대한 동영상 시청 기록을 개별 조회, 갱신, 삭제합니다.
    - 권한: 인증된 사용자 중 수퍼유저만이 동영상 시청 기록을 개별 조회, 갱신, 삭제할 수 있습니다.
    """

    queryset = VideoEventData.objects.all()
    serializer_class = VideoEventDataSerializer
    permission_classes = [IsSuperUser]
    lookup_url_kwarg = "event_id"

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        video_id = self.kwargs["video_id"]
        event_id = self.kwargs["event_id"]

        return VideoEventData.objects.filter(
            user__id=user_id, video__id=video_id, id=event_id
        )

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if not obj:
            raise NotFound("해당 시청 기록을 찾을 수 없습니다.")
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
