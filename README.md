# Django-Jitsi

Panel de administración para gestionar solicitudes de alta de usuarios que podrán utilizar Jitsi Meet.

## Descripción

Django-Jitsi es una aplicación web desarrollada en Django que permite a los administradores gestionar las solicitudes de registro de usuarios que desean acceder a reuniones de Jitsi Meet. El flujo de trabajo incluye:

1. Los usuarios envían solicitudes de registro
2. Los administradores revisan las solicitudes
3. Aproban o rechazan las solicitudes
4. (Opcional) Envío de invitaciones o activación de cuentas

## Stack Tecnológico

- **Backend**: Django 5.x
- **Base de datos**: SQLite (desarrollo)
- **Servidor**: Gunicorn
- **Contenedores**: Docker + Docker Compose
- **Proxy reverso**: Nginx (opcional, para producción)
- **Testing**: pytest + Django Test Framework

## Características

- Panel de administración para gestionar solicitudes de usuarios
- Sistema de estados: pendiente, aprobado, rechazado
- Creación automática de usuarios al aprobar solicitudes
- Dashboard con métricas y estadísticas
- Integración con Jitsi Meet (generación de JWT y links de reunión)
- Tests completos con pytest y Django Test Framework
- Entorno completamente containerizado

## Roadmap de Integración con Jitsi

### Fase 1 (MVP) - ✅ COMPLETADO
- Solo gestión de solicitudes y usuarios
- Sin integración directa con Jitsi

### Fase 2 - ✅ COMPLETADO
- Generación de links de reunión
- Soporte para JWT si el despliegue de Jitsi usa "secure domain"

### Fase 3 - ✅ PREPARADO
- Sincronización con Prosody/Jitsi vía módulos o API

## Instalación y Uso

### Prerrequisitos

- Docker
- Docker Compose

### Configuración inicial

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd jitsi-django
```

2. Copia el archivo de variables de entorno:
```bash
cp env.example .env
```

3. Edita las variables en `.env` según tus necesidades:
```env
DJANGO_SECRET_KEY=tu_clave_secreta_aqui
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=*
DJANGO_SUPERUSER_EMAIL=admin@tudominio.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=tu_password_seguro

# Configuración para Jitsi
JITSI_BASE_URL=https://meet.tudominio.com
JITSI_JWT_SECRET=tu_clave_jwt_secreta
JITSI_APP_ID=django-jitsi
```

### Inicio rápido

```bash
# Ejecutar setup completo con tests
./test_setup.sh
```

O manualmente:

```bash
# Construir y ejecutar
docker compose build
docker compose up -d

# Crear migraciones
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Acceder al panel de administración
# http://localhost:8000/admin
```

### Crear solicitudes de prueba

```bash
docker compose exec web python manage.py shell -c \
"from accounts.models import SignupRequest as S; \
 S.objects.create(email='alice@example.com', full_name='Alice'); \
 S.objects.create(email='bob@example.com', full_name='Bob', note='Equipo Ventas')"
```

## Testing

### Ejecutar todos los tests

```bash
# Ejecutar tests con pytest y Django
./run_tests.sh
```

### Tests individuales

```bash
# Solo tests con pytest
docker compose exec web python -m pytest src/accounts/tests.py -v

# Solo tests con Django
docker compose exec web python manage.py test accounts.tests

# Tests específicos
docker compose exec web python -m pytest src/accounts/tests.py::SignupRequestModelTest -v
```

### Probar integración con Jitsi

```bash
# Probar funcionalidades de Jitsi
./test_jitsi_integration.sh
```

## Estructura del Proyecto

```
django-jitsi/
├─ compose.yml                    # Docker Compose
├─ env.example                    # Variables de entorno ejemplo
├─ test_setup.sh                  # Script de setup completo
├─ run_tests.sh                   # Script para ejecutar tests
├─ test_jitsi_integration.sh      # Script para probar Jitsi
├─ pytest.ini                    # Configuración de pytest
├─ docker/
│  ├─ web.Dockerfile             # Imagen Docker
│  ├─ entrypoint.sh              # Script de inicio
│  └─ requirements.txt           # Dependencias Python
└─ src/
   ├─ manage.py
   ├─ config/                    # Configuración principal de Django
   │  ├─ settings.py
   │  ├─ urls.py
   │  └─ wsgi.py
   └─ accounts/                  # Aplicación para manejo de solicitudes/usuarios
      ├─ models.py               # Modelos SignupRequest y Meeting
      ├─ admin.py                # Configuración del panel admin
      ├─ views.py                # Vistas del dashboard
      ├─ urls.py                 # URLs de la aplicación
      ├─ forms.py                # Formularios
      ├─ jitsi.py                # Integración con Jitsi
      ├─ tests.py                # Tests completos
      └─ templates/              # Plantillas HTML
         └─ accounts/
            ├─ dashboard.html
            ├─ request_list.html
            └─ request_detail.html
```

## Funcionalidades de Jitsi

### Generación de JWT

```python
from accounts.jitsi import jitsi_jwt

# Generar token JWT para una sala
token = jitsi_jwt(room="mi-sala", user_name="Usuario")
```

### Creación de links de reunión

```python
from accounts.jitsi import generate_meeting_link

# Crear link de reunión
link = generate_meeting_link("mi-sala", "Usuario")
# Resultado: https://meet.example.com/mi-sala?jwt=...
```

### Gestión de reuniones

```python
from accounts.models import Meeting
from django.utils import timezone

# Crear una reunión
meeting = Meeting.objects.create(
    room_name="reunion-importante",
    owner=user,
    start_time=timezone.now()
)

# Generar link de la reunión
link = meeting.generate_jitsi_link()
```

## Desarrollo

### Ejecutar en modo desarrollo

```bash
docker compose up
```

### Acceder al shell de Django

```bash
docker compose exec web python manage.py shell
```

### Crear migraciones

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Ejecutar tests durante desarrollo

```bash
# Tests rápidos
docker compose exec web python -m pytest src/accounts/tests.py::SignupRequestModelTest -v

# Todos los tests
./run_tests.sh
```

## Configuración de Producción

### Variables de entorno para producción

```env
DJANGO_SECRET_KEY=clave_super_secreta_produccion
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Configuración Jitsi
JITSI_BASE_URL=https://meet.tu-dominio.com
JITSI_JWT_SECRET=clave_jwt_super_secreta
JITSI_APP_ID=tu-app-id
```

### Configurar Jitsi con JWT

1. Configura tu servidor Jitsi para aceptar JWT
2. Establece las variables de entorno correspondientes
3. El sistema generará automáticamente tokens JWT para las reuniones

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Ejecuta los tests (`./run_tests.sh`)
4. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
5. Push a la rama (`git push origin feature/AmazingFeature`)
6. Abre un Pull Request

## Tests Implementados

- ✅ Tests de modelos (SignupRequest, Meeting)
- ✅ Tests de admin actions (aprobar/rechazar solicitudes)
- ✅ Tests de vistas (dashboard, lista, detalle)
- ✅ Tests de integración con Jitsi
- ✅ Tests de generación de JWT
- ✅ Tests de creación de links de reunión
- ✅ Tests con pytest y Django Test Framework

## Licencia

Este proyecto está licenciado bajo la Licencia Pública General de GNU v3.0 - ver el archivo [LICENSE](LICENSE) para más detalles.

## Plan de Desarrollo

Para más detalles sobre el plan de desarrollo por fases, consulta el archivo `plans/original.md` en el repositorio.

## Estado del Proyecto

🎉 **PROYECTO COMPLETADO** - Todas las 9 fases implementadas con tests completos

- ✅ Fase 1: Estructura mínima del repositorio
- ✅ Fase 2: Variables de entorno
- ✅ Fase 3: Docker & Compose
- ✅ Fase 4: Proyecto Django base
- ✅ Fase 5: Modelo de Solicitudes y admin
- ✅ Fase 6: Vistas mínimas y templates
- ✅ Fase 7: Primer arranque y pruebas
- ✅ Fase 8: Roadmap Jitsi (integración)
- ✅ Fase 9: Tests básicos