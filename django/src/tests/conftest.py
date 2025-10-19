import os
import django
from django.conf import settings

# Configurar Django para los tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
