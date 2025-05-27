from django.urls import path
from .views import HomeView, BulkUploadWebView, ImageUploadWebView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("upload/", ImageUploadWebView.as_view(), name="upload"),
    path("test-load/", BulkUploadWebView.as_view(), name="test-load"),
]
