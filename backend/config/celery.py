"""Flux Celery configuration."""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('flux')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'poll-all-inboxes': {
        'task': 'apps.tickets.tasks.poll_all_inboxes',
        'schedule': 30.0,
    },
    'check-escalations': {
        'task': 'apps.tickets.tasks.check_escalations',
        'schedule': 300.0,
    },
    'auto-close-resolved': {
        'task': 'apps.tickets.tasks.auto_close_resolved',
        'schedule': 86400.0,
    },
}
