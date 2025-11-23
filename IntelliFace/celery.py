import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IntelliFace.settings")

app = Celery("IntelliFace")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()