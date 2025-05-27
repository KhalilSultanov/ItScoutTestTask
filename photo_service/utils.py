from PIL import Image, UnidentifiedImageError
from io import BytesIO
from pathlib import Path


def validate_image_file(image_file, image_bytes):
    allowed_mime = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"}
    allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

    if image_file.content_type not in allowed_mime:
        raise ValueError("Недопустимый MIME-тип файла.")

    ext = Path(image_file.name).suffix.lower()
    if ext not in allowed_ext:
        raise ValueError("Недопустимое расширение файла.")

    try:
        img = Image.open(BytesIO(image_bytes))
        img.verify()
    except UnidentifiedImageError:
        raise ValueError("Загруженный файл не является корректным изображением.")
