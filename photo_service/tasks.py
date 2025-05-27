import os
import time
import random
import logging
import redis
import requests

from celery import shared_task
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from .models import UploadedImage

logger = logging.getLogger(__name__)

r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
)


def notify_telegram(chat_id: str, message: str):
    try:
        response = requests.post(
            TELEGRAM_API_URL,
            data={
                "chat_id": chat_id,
                "text": message,
            },
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Telegram notification failed: {e}")


@shared_task
def process_image_task(image_data: bytes, original_name: str):
    time.sleep(20)
    result = random.randint(1, 1000)

    unique_name = f"{random.randint(1000, 9999)}_{original_name}"
    file = ContentFile(image_data, name=unique_name)

    UploadedImage.objects.create(image=file, result=result, uploaded_at=timezone.now())

    global_count = r.incr("uploaded_images:count")

    batch = (global_count - 1) // 100
    key = f"notified:{batch}:20"

    if global_count % 100 == 20:
        was_notified = r.setnx(key, 1)
        if was_notified:
            notify_telegram(
                str(os.environ.get("TELEGRAM_CHAT_ID")), f"Обработано 20 изображений"
            )
