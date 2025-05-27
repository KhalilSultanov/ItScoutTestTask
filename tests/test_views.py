import pytest
from django.urls import reverse
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


def generate_valid_image_bytes():
    img_bytes = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="red")
    image.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.mark.django_db
def test_api_upload_success(client):
    valid_image = SimpleUploadedFile(
        "test.jpg", generate_valid_image_bytes(), content_type="image/jpeg"
    )
    with patch("photo_service.views.process_image_task.delay") as mocked:
        response = client.post(reverse("api-upload"), {"image": valid_image})
    assert response.status_code == 202
    mocked.assert_called_once()


def test_api_upload_no_file(client):
    response = client.post(reverse("api-upload"), {})
    assert response.status_code == 400
    assert "No image uploaded" in response.json()["error"]


def test_api_upload_invalid_content_type(client):
    bad_file = SimpleUploadedFile(
        "test.txt", b"not an image", content_type="text/plain"
    )
    response = client.post(reverse("api-upload"), {"image": bad_file})
    assert response.status_code == 400
    assert "Unsupported MIME type" in response.json()["error"]


def test_api_upload_invalid_image_content(client):
    bad_image = SimpleUploadedFile(
        "test.jpg", b"not really an image", content_type="image/jpeg"
    )
    response = client.post(reverse("api-upload"), {"image": bad_image})
    assert response.status_code == 400
    assert "not a valid image" in response.json()["error"].lower()


@pytest.mark.django_db
def test_api_bulk_upload_success(client):
    valid_image = SimpleUploadedFile(
        "test.jpg", generate_valid_image_bytes(), content_type="image/jpeg"
    )
    with patch("photo_service.views.process_image_task.delay") as mocked:
        response = client.post(reverse("api-bulk-upload"), {"image": valid_image})
    assert response.status_code == 202
    assert mocked.call_count == 100


def test_api_bulk_upload_no_file(client):
    response = client.post(reverse("api-bulk-upload"), {})
    assert response.status_code == 400
    assert "No file uploaded" in response.json()["error"]


def test_api_bulk_upload_invalid_file(client):
    bad_image = SimpleUploadedFile("bad.png", b"not image", content_type="image/png")
    response = client.post(reverse("api-bulk-upload"), {"image": bad_image})
    assert response.status_code == 400
    assert "not a valid image" in response.json()["error"].lower()
