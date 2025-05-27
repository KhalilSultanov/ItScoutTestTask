from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from .tasks import process_image_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadedImage
from .utils import validate_image_file


@extend_schema(
    summary="Загрузка одного изображения",
    description="Загружает изображение и запускает фоновую обработку через Celery.",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {"image": {"type": "string", "format": "binary"}},
        }
    },
    responses={
        202: OpenApiResponse(description="Изображение принято в обработку"),
        400: OpenApiResponse(description="Файл не загружен"),
        500: OpenApiResponse(description="Ошибка сервера"),
    },
)
class ImageUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "No image uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_bytes = image_file.read()
            validate_image_file(image_file, image_bytes)
            process_image_task.delay(image_bytes, image_file.name)
            return Response({"status": "accepted"}, status=status.HTTP_202_ACCEPTED)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_protect, name="dispatch")
class ImageUploadWebView(View):
    def post(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            return render(
                request,
                "upload/home.html",
                {
                    "images": UploadedImage.objects.all().order_by("-id"),
                    "error": "No file uploaded",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            image_bytes = image_file.read()
            validate_image_file(image_file, image_bytes)
            process_image_task.delay(image_bytes, image_file.name)
            return redirect("/?refresh=1")
        except ValueError as ve:
            return render(
                request,
                "upload/home.html",
                {
                    "images": UploadedImage.objects.all().order_by("-id"),
                    "error": str(ve),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return render(
                request,
                "upload/home.html",
                {
                    "images": UploadedImage.objects.all().order_by("-id"),
                    "error": "Server error: " + str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class BulkUploadWebView(View):
    def post(self, request):
        image_file = request.FILES.get("image")
        images = UploadedImage.objects.all().order_by("-id")

        if not image_file:
            return render(
                request,
                "upload/home.html",
                {"images": images, "error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            image_bytes = image_file.read()
            validate_image_file(image_file, image_bytes)
            for _ in range(100):
                process_image_task.delay(image_bytes, image_file.name)
            return redirect("/?refresh=1")
        except ValueError as ve:
            return render(
                request,
                "upload/home.html",
                {"images": images, "error": str(ve)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return render(
                request,
                "upload/home.html",
                {"images": images, "error": "Server error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    summary="Пакетная загрузка изображения (x100)",
    description="Загружает изображение и запускает его обработку 100 раз в фоне через Celery.",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {"image": {"type": "string", "format": "binary"}},
        }
    },
    responses={
        202: OpenApiResponse(description="Изображения отправлены в обработку"),
        400: OpenApiResponse(description="Файл не загружен"),
        500: OpenApiResponse(description="Ошибка сервера"),
    },
)
class BulkUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_bytes = image_file.read()
            validate_image_file(image_file, image_bytes)
            for _ in range(100):
                process_image_task.delay(image_bytes, image_file.name)
            return Response(
                {"status": "bulk accepted"}, status=status.HTTP_202_ACCEPTED
            )
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HomeView(View):
    def get(self, request):
        images = UploadedImage.objects.all().order_by("-id")
        return render(request, "upload/home.html", {"images": images})
