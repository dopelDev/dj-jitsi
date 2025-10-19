#!/usr/bin/env bash
set -euo pipefail

echo "Starting Django-Jitsi application..."

# Crear directorio de base de datos si no existe
python - <<'PY'
import os, pathlib
from dotenv import load_dotenv
load_dotenv()
pathlib.Path('db').mkdir(exist_ok=True)
print("Database directory created/verified")
PY

echo "Running database migrations..."
python manage.py migrate --noinput

# Crea superuser idempotente si no existe
echo "Creating superuser if needed..."
python - <<'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
u = os.environ.get("DJANGO_SUPERUSER_USERNAME")
p = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
e = os.environ.get("DJANGO_SUPERUSER_EMAIL")
if u and p and e and not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print(f"Superuser {u} created successfully")
else:
    print("Superuser already exists or credentials not provided")
PY

echo "Starting Django development server..."
# runserver (dev) o gunicorn (prod). Para MVP: runserver.
exec python manage.py runserver 0.0.0.0:8000
