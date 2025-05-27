import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

worker_send_task_events = True
task_send_sent_event = True

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
