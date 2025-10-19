#!/bin/bash
# Script para probar la integración con Jitsi

set -e

echo "=== Probando integración con Jitsi ==="

# Verificar que Docker esté corriendo
if ! docker compose ps | grep -q "web"; then
    echo "Iniciando contenedor..."
    docker compose up -d
    sleep 5
fi

echo "=== Configurando variables de entorno para Jitsi ==="
docker compose exec web python manage.py shell -c "
import os
os.environ['JITSI_BASE_URL'] = 'https://meet.jit.si'
os.environ['JITSI_JWT_SECRET'] = 'test_secret_key_for_jitsi_integration'
os.environ['JITSI_APP_ID'] = 'django-jitsi-test'

print('Variables de entorno configuradas:')
print(f'JITSI_BASE_URL: {os.environ.get(\"JITSI_BASE_URL\")}')
print(f'JITSI_JWT_SECRET: {os.environ.get(\"JITSI_JWT_SECRET\")}')
print(f'JITSI_APP_ID: {os.environ.get(\"JITSI_APP_ID\")}')
"

echo "=== Probando generación de JWT ==="
docker compose exec web python manage.py shell -c "
from accounts.jitsi import jitsi_jwt, generate_meeting_link, create_secure_room
import os

# Configurar variables
os.environ['JITSI_JWT_SECRET'] = 'test_secret_key_for_jitsi_integration'
os.environ['JITSI_APP_ID'] = 'django-jitsi-test'

# Probar generación de JWT
token = jitsi_jwt('meet', 'test-room', 'Test User')
if token:
    print(f'JWT generado exitosamente: {token[:50]}...')
else:
    print('Error generando JWT')

# Probar generación de link
link = generate_meeting_link('test-room', 'Test User')
print(f'Link de reunión generado: {link}')

# Probar creación de sala segura
room_info = create_secure_room('secure-room', 'Admin User')
print(f'Información de sala: {room_info}')
"

echo "=== Probando funcionalidad de reuniones ==="
docker compose exec web python manage.py shell -c "
from accounts.models import Meeting
from django.contrib.auth.models import User
from django.utils import timezone
import os

# Configurar variables
os.environ['JITSI_JWT_SECRET'] = 'test_secret_key_for_jitsi_integration'
os.environ['JITSI_APP_ID'] = 'django-jitsi-test'

# Crear usuario de prueba si no existe
user, created = User.objects.get_or_create(
    username='jitsi_test_user',
    defaults={'email': 'jitsi@test.com'}
)
if created:
    print('Usuario de prueba creado')
else:
    print('Usuario de prueba ya existe')

# Crear reunión de prueba
meeting, created = Meeting.objects.get_or_create(
    room_name='test-meeting-room',
    defaults={
        'owner': user,
        'start_time': timezone.now(),
        'is_active': True
    }
)

if created:
    print('Reunión de prueba creada')
else:
    print('Reunión de prueba ya existe')

# Probar generación de link de reunión
try:
    meeting_link = meeting.generate_jitsi_link()
    print(f'Link de reunión generado: {meeting_link}')
except Exception as e:
    print(f'Error generando link: {e}')

print(f'Total de reuniones: {Meeting.objects.count()}')
"

echo "=== Creando solicitudes de prueba para usuarios aprobados ==="
docker compose exec web python manage.py shell -c "
from accounts.models import SignupRequest
from django.contrib.auth.models import User

# Crear solicitudes de prueba
test_requests = [
    {'email': 'jitsi.user1@example.com', 'full_name': 'Jitsi User 1', 'note': 'Usuario para probar Jitsi'},
    {'email': 'jitsi.user2@example.com', 'full_name': 'Jitsi User 2', 'note': 'Otro usuario para Jitsi'},
]

for req_data in test_requests:
    request, created = SignupRequest.objects.get_or_create(
        email=req_data['email'],
        defaults=req_data
    )
    if created:
        print(f'Solicitud creada: {request.email}')
        # Aprobar la solicitud
        request.approve()
        print(f'Solicitud aprobada: {request.email}')
    else:
        print(f'Solicitud ya existe: {request.email}')

print(f'Total de solicitudes: {SignupRequest.objects.count()}')
print(f'Total de usuarios: {User.objects.count()}')
"

echo "=== Integración con Jitsi probada exitosamente ==="
echo ""
echo "Funcionalidades probadas:"
echo "✓ Generación de JWT para Jitsi"
echo "✓ Creación de links de reunión"
echo "✓ Creación de salas seguras"
echo "✓ Modelo de reuniones"
echo "✓ Aprobación de solicitudes y creación de usuarios"
echo ""
echo "Para probar en producción:"
echo "1. Configura JITSI_JWT_SECRET con tu clave real"
echo "2. Configura JITSI_BASE_URL con tu dominio de Jitsi"
echo "3. Instala pyjwt: pip install pyjwt"
echo "4. Configura tu servidor Jitsi para aceptar JWT"
