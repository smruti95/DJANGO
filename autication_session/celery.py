import os
import redis.connection
from celery import Celery
try:
    _orig_conn_init = redis.connection.Connection.__init__
    def _patched_conn_init(self, *args, **kwargs):
        kwargs['protocol'] = 2
        kwargs.pop('maint_notifications', None)
        _orig_conn_init(self, *args, **kwargs)
    redis.connection.Connection.__init__ = _patched_conn_init
    if hasattr(redis.connection, 'MaintNotificationsAbstractConnection'):
        redis.connection.MaintNotificationsAbstractConnection._configure_maintenance_notifications = lambda *a, **k: None
except Exception:
    pass

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autication_session.settings')

app = Celery('autication_session')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()


