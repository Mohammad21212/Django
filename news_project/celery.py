from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default settings for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')

# Create an instance of Celery
app = Celery('news_project')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
