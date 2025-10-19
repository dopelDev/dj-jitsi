#!/bin/bash
# Script para configurar y probar el entorno de desarrollo

set -e

echo "=== Configurando entorno Django-Jitsi ==="

# Crear archivo .env desde ejemplo
if [ ! -f .env ]; then
    cp env.example .env
    echo "Archivo .env creado desde env.example"
else
    echo "Archivo .env ya existe"
fi

# Crear directorio de base de datos
mkdir -p db

echo "=== Construyendo imagen Docker ==="
docker compose build

echo "=== Ejecutando migraciones ==="
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate

echo "=== Creando superusuario ==="
docker compose run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
u = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print(f'Superusuario {u} creado exitosamente')
else:
    print(f'Superusuario {u} ya existe')
"

echo "=== Creando solicitudes de prueba ==="
docker compose run --rm web python manage.py shell -c "
from accounts.models import SignupRequest as S
# Crear solicitudes de prueba si no existen
if S.objects.count() == 0:
    S.objects.create(email='alice@example.com', full_name='Alice Johnson', note='Equipo de desarrollo')
    S.objects.create(email='bob@example.com', full_name='Bob Smith', note='Equipo de ventas')
    S.objects.create(email='carol@example.com', full_name='Carol Davis', note='Equipo de marketing')
    print('Solicitudes de prueba creadas exitosamente')
else:
    print('Ya existen solicitudes en la base de datos')
"

echo "=== Iniciando servidor ==="
echo "El servidor estará disponible en: http://localhost:8000"
echo "Admin disponible en: http://localhost:8000/admin"
echo "Dashboard disponible en: http://localhost:8000"
echo ""
echo "Credenciales por defecto:"
echo "Usuario: admin"
echo "Password: admin123"
echo ""
echo "Presiona Ctrl+C para detener el servidor"

docker compose up
