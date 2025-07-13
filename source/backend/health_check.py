#!/usr/bin/env python3
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings.staging")
django.setup()
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connection OK")
    sys.exit(0)
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
