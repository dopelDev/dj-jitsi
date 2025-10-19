# Django-Jitsi Integration

Sistema integrado de Django con Jitsi Meet para gestión de usuarios y videoconferencias seguras.

## Estructura del Proyecto

```
jitsi-django/
├── django/                    # Aplicación Django (con venv)
│   ├── src/                   # Código Django
│   ├── db/                    # Base de datos SQLite
│   ├── requirements.txt       # Dependencias Python
│   └── README.md             # Documentación Django
├── jitsi/                     # Servidor Jitsi (con Docker)
│   ├── docker-compose.yml    # Configuración Docker
│   ├── config/               # Configuraciones Jitsi
│   └── README.md             # Documentación Jitsi
├── .gitignore               # Git ignore actualizado
└── LICENSE
```

## Características

- **Django**: Gestión de usuarios, solicitudes de registro, creación de reuniones
- **Jitsi**: Servidor de videoconferencias con autenticación JWT
- **Separación clara**: Django con virtual environment, Jitsi con Docker
- **Integración segura**: JWT para autenticación en reuniones

## Setup Rápido

### 1. Django (Virtual Environment)

```bash
cd django
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### 2. Jitsi (Docker)

```bash
cd jitsi
cp .env.example .env
docker-compose up -d
```

## Funcionalidades

### Django
- **Solicitudes de Registro**: Los usuarios pueden solicitar acceso
- **Gestión de Usuarios**: Administradores aprueban/rechazan solicitudes
- **Creación de Reuniones**: Usuarios registrados crean salas Jitsi
- **Sistema de Roles**: USER, WEB_ADMIN, ENV_ADMIN, GUEST

### Jitsi
- **Servidor Completo**: Prosody + Jicofo + JVB + Nginx
- **Autenticación JWT**: Reuniones seguras con tokens
- **P2P Optimizado**: Configuración STUN/TURN para conexiones directas
- **Proxy Reverso**: Nginx con SSL para acceso seguro

## Acceso

- **Django**: `http://localhost:8000`
- **Jitsi Meet**: `https://localhost:8443`
- **Admin Django**: `http://localhost:8000/admin/`

## Documentación Detallada

- [Django Setup](django/README.md) - Configuración con virtual environment
- [Jitsi Setup](jitsi/README.md) - Configuración con Docker

## Tecnologías

- **Django 5.x**: Framework web Python
- **Jitsi Meet**: Plataforma de videoconferencias
- **Docker**: Containerización de Jitsi
- **SQLite**: Base de datos para desarrollo
- **JWT**: Autenticación segura
- **WebRTC**: Comunicación peer-to-peer

## Desarrollo

### Django
- Usa virtual environment (sin Docker)
- Base de datos SQLite para desarrollo
- Tests con pytest

### Jitsi
- Completamente containerizado
- Configuración consolidada en docker-compose.yml
- Logs centralizados

## Licencia

Ver [LICENSE](LICENSE) para más detalles.