import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

# Create a Celery instance
app = Celery('billify')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')
from integrations.sync.tasks import add

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': add,
        'schedule': 30.0,  # Run every 30 seconds
        'args': (16, 16),  # Arguments for the task
    },
}
