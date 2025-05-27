from django.urls import path
from .views import ImageUploadAPIView, BulkUploadAPIView

urlpatterns = [
    path("upload/", ImageUploadAPIView.as_view(), name="api-upload"),
    path("test-load/", BulkUploadAPIView.as_view(), name="api-bulk-upload"),
]
