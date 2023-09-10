import os
import celery

from django.conf import settings

from main import sentry


class Celery(celery.Celery):
    def on_configure(self):
        if settings.SENTRY_ENABLED:
            sentry.init_sentry(**settings.SENTRY_CONFIG)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.autodiscover_tasks(['main'])


# This is used for ECS Cluster (Each queue needs it's own clusters)
class CeleryQueue():
    DEFAULT = 'CELERY-DEFAULT-QUEUE'
    EXPORT_HEAVY = 'CELERY-EXPORT-HEAVY-QUEUE'

    ALL_QUEUES = (
        DEFAULT,
        EXPORT_HEAVY,
    )


app.conf.task_default_queue = CeleryQueue.DEFAULT


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
