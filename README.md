# 🎥 Jitsi-Django Integration

Sistema completo de videoconferencias integrado con Django para gestión de usuarios y reuniones seguras.

## 📋 Descripción del Proyecto

Este proyecto combina una aplicación Django para gestión de usuarios con un servidor Jitsi Meet para videoconferencias, proporcionando una solución completa para organizaciones que necesitan control de acceso y gestión de reuniones.

### 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐
│   Django App    │    │   Jitsi Meet    │
│   (Puerto 8000) │◄──►│  (Puerto 8080)  │
│                 │    │                 │
│ • Gestión Users │    │ • Videoconf     │
│ • Auth JWT      │    │ • WebRTC        │
│ • Reuniones     │    │ • P2P/STUN      │
└─────────────────┘    └─────────────────┘
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- Docker y Docker Compose
- Git

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd jitsi-django
```

### 2. Configurar Django

```bash
# Navegar al directorio Django
cd django

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Configurar base de datos
python src/manage.py migrate
python src/manage.py createsuperuser

# Ejecutar Django
python src/manage.py runserver
```

### 3. Configurar Jitsi

```bash
# Navegar al directorio Jitsi
cd ../jitsi

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Ejecutar Jitsi con Docker
docker-compose up -d
```

### 4. Acceder a las Aplicaciones

- **Django Admin**: http://localhost:8000/admin/
- **Django App**: http://localhost:8000/
- **Jitsi Meet**: http://localhost:8080/

## 🎯 Funcionalidades Principales

### Django (Gestión de Usuarios)

- **Sistema de Roles**: USER, WEB_ADMIN, ENV_ADMIN, GUEST
- **Solicitudes de Registro**: Los usuarios pueden solicitar acceso
- **Gestión de Usuarios**: Administradores aprueban/rechazan solicitudes
- **Creación de Reuniones**: Usuarios registrados crean salas Jitsi
- **Autenticación JWT**: Tokens seguros para acceso a reuniones

### Jitsi Meet (Videoconferencias)

- **Servidor Completo**: Prosody + Jicofo + JVB + Nginx
- **WebRTC**: Comunicación peer-to-peer optimizada
- **STUN/TURN**: Configuración para conexiones directas
- **SSL/TLS**: Conexiones seguras
- **Sin Autenticación**: Configurado para desarrollo

## 📁 Estructura del Proyecto

```
jitsi-django/
├── django/                          # Aplicación Django
│   ├── src/                         # Código fuente Django
│   │   ├── config/                  # Configuración Django
│   │   ├── models/                  # Modelos de datos
│   │   ├── views/                   # Vistas y formularios
│   │   ├── templates/               # Plantillas HTML
│   │   └── utils/                   # Utilidades (Jitsi)
│   ├── db/                          # Base de datos SQLite
│   ├── venv/                        # Entorno virtual Python
│   ├── requirements.txt             # Dependencias Python
│   └── README.md                    # Documentación Django
├── jitsi/                           # Servidor Jitsi
│   ├── config/                      # Configuraciones Jitsi
│   ├── logs/                        # Logs del servidor
│   ├── docker-compose.yml           # Configuración Docker
│   ├── Dockerfile                   # Imagen personalizada
│   └── README.md                    # Documentación Jitsi
├── LICENSE                          # Licencia del proyecto
└── README.md                        # Este archivo
```

## ⚙️ Configuración Detallada

### Variables de Entorno Django

```bash
# django/.env
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
JITSI_BASE_URL=http://localhost:8080
```

### Variables de Entorno Jitsi

```bash
# jitsi/.env
JITSI_DOMAIN=localhost
PUBLIC_URL=http://localhost:8080
ENABLE_AUTH=false
ENABLE_GUESTS=1
ENABLE_WELCOME_PAGE=1
```

## 🔧 Desarrollo

### Django

```bash
cd django
source venv/bin/activate

# Ejecutar tests
python -m pytest

# Crear migraciones
python src/manage.py makemigrations

# Aplicar migraciones
python src/manage.py migrate

# Crear superusuario
python src/manage.py createsuperuser
```

### Jitsi

```bash
cd jitsi

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache
```

## 🔗 Integración Django-Jitsi

### Creación de Reuniones

```python
# En Django, crear una reunión
from utils.jitsi import create_meeting_url

def create_meeting(room_name, user_name):
    return create_meeting_url(room_name, user_name)
```

### Autenticación JWT (Futuro)

```python
# Configuración para autenticación JWT
JITSI_CONFIG = {
    'DOMAIN': 'localhost',
    'JWT_SECRET': 'tu-secreto-jwt',
    'ENABLE_AUTH': True,
}
```

## 🛠️ Troubleshooting

### Problemas Comunes

#### Django no inicia
```bash
# Verificar dependencias
pip install -r requirements.txt

# Verificar base de datos
python src/manage.py migrate

# Verificar variables de entorno
cat .env
```

#### Jitsi no accesible
```bash
# Verificar contenedor
docker-compose ps

# Ver logs
docker-compose logs

# Verificar puertos
netstat -tulpn | grep :8080
```

#### Problemas de conectividad
- Verificar que ambos servicios estén ejecutándose
- Comprobar configuración de URLs en Django
- Revisar logs de ambos servicios

## 📚 Documentación Adicional

- [Django Setup](django/README.md) - Configuración detallada de Django
- [Jitsi Setup](jitsi/README.md) - Configuración detallada de Jitsi
- [Django Documentation](https://docs.djangoproject.com/)
- [Jitsi Meet Documentation](https://jitsi.org/docs/)

## 🧪 Testing

### Django Tests

```bash
cd django
source venv/bin/activate
python -m pytest
```

### Jitsi Tests

```bash
cd jitsi
# Verificar que el contenedor esté funcionando
curl http://localhost:8080
```

## 🚀 Despliegue

### Desarrollo

1. Django en puerto 8000
2. Jitsi en puerto 8080
3. Base de datos SQLite
4. Sin SSL (HTTP)

### Producción

1. Configurar dominio real
2. Habilitar SSL/TLS
3. Configurar base de datos PostgreSQL
4. Habilitar autenticación JWT
5. Configurar proxy reverso

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

Para soporte y preguntas:

1. Revisar la documentación
2. Verificar logs de ambos servicios
3. Crear issue en el repositorio
4. Contactar al equipo de desarrollo

---

**Nota**: Este es un proyecto de desarrollo. Para producción, configurar SSL, autenticación JWT y base de datos robusta.