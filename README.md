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

## Características

- Panel de administración para gestionar solicitudes de usuarios
- Sistema de estados: pendiente, aprobado, rechazado
- Creación automática de usuarios al aprobar solicitudes
- Dashboard con métricas y estadísticas
- Integración futura con Jitsi Meet (generación de JWT y links de reunión)

## Roadmap de Integración con Jitsi

### Fase 1 (MVP)
- Solo gestión de solicitudes y usuarios
- Sin integración directa con Jitsi

### Fase 2
- Generación de links de reunión
- Soporte para JWT si el despliegue de Jitsi usa "secure domain"

### Fase 3
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
cp .env.example .env
```

3. Edita las variables en `.env` según tus necesidades:
```env
DJANGO_SECRET_KEY=tu_clave_secreta_aqui
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=*
DJANGO_SUPERUSER_EMAIL=admin@tudominio.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=tu_password_seguro
```

4. Construye y ejecuta los contenedores:
```bash
docker compose build
docker compose up -d
```

5. Accede al panel de administración:
```
http://localhost:8000/admin
```

### Crear solicitudes de prueba

```bash
docker compose exec web python manage.py shell -c \
"from accounts.models import SignupRequest as S; \
 S.objects.create(email='alice@example.com', full_name='Alice'); \
 S.objects.create(email='bob@example.com', full_name='Bob', note='Equipo Ventas')"
```

## Estructura del Proyecto

```
django-jitsi/
├─ compose.yml
├─ .env.example
├─ .env              # (no se incluye en el repositorio)
├─ docker/
│  ├─ web.Dockerfile
│  ├─ entrypoint.sh
│  └─ requirements.txt
└─ src/
   ├─ manage.py
   ├─ config/        # Configuración principal de Django
   └─ accounts/      # Aplicación para manejo de solicitudes/usuarios
      ├─ models.py   # Modelo SignupRequest
      ├─ admin.py    # Configuración del panel admin
      ├─ views.py    # Vistas del dashboard
      ├─ urls.py     # URLs de la aplicación
      └─ templates/  # Plantillas HTML
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

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia Pública General de GNU v3.0 - ver el archivo [LICENSE](LICENSE) para más detalles.

## Plan de Desarrollo

Para más detalles sobre el plan de desarrollo por fases, consulta el archivo `plans/original.md` en el repositorio.
