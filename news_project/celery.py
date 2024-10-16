from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

CONFIG = {
    'DJANGO_SETTINGS_MODULE': 'news_project.settings',
    'CELERY_APP_NAME': 'news_project',
    'CELERY_NAMESPACE': 'CELERY',
    'BROKER_CONNECTION_RETRY_ON_STARTUP': True,
}

os.environ.setdefault('DJANGO_SETTINGS_MODULE', CONFIG['DJANGO_SETTINGS_MODULE'])

app = Celery(CONFIG['CELERY_APP_NAME'])

app.config_from_object('django.conf:settings', namespace=CONFIG['CELERY_NAMESPACE'])
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = CONFIG['BROKER_CONNECTION_RETRY_ON_STARTUP']


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
