# backend/django_app/celery.py

import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

app = Celery('django_app')

# Using Redis as broker
app.config_from_object('django.conf:settings', namespace='CELERY')

# ✅ Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# ✅ AJOUTER seo_analyzer explicitement si besoin
app.autodiscover_tasks(['integrations.openai', 'seo_analyzer','file_converter'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')