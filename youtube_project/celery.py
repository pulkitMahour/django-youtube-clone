from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_project.settings')

app = Celery('youtube_project')

app.conf.enable_utc = False

app.conf.update(timezone='Asia/Kolkata')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
	'send-mail-every-day-at-5': {
		'task': 'youtube_app.task.mail_to_subscribers',
		'schedule': crontab(hour=17,minute=0),
	}
}

@app.task(bind=True)

def debug_task(self):
	print(f'Request: {self.request|r}')