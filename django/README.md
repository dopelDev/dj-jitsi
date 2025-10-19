# Django Jitsi Integration

Aplicación Django para integración con Jitsi Meet, incluyendo gestión de usuarios, solicitudes de registro y creación de reuniones.

## Setup con Virtual Environment

### 1. Crear Virtual Environment

```bash
cd django
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 4. Configurar Base de Datos

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ejecutar Servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://localhost:8000`

## Funcionalidades

- **Solicitudes de Registro**: Los usuarios pueden solicitar acceso al sistema
- **Gestión de Usuarios**: Administradores pueden aprobar/rechazar solicitudes
- **Creación de Reuniones**: Usuarios registrados pueden crear salas Jitsi
- **Roles de Usuario**: Sistema de roles (USER, WEB_ADMIN, ENV_ADMIN, GUEST)

## Integración con Jitsi

La aplicación se conecta con el servidor Jitsi local (puerto 8443) para crear reuniones seguras con JWT.

## Estructura del Proyecto

```
django/
├── src/                    # Código Django
│   ├── accounts/          # App de usuarios y reuniones
│   └── config/            # Configuración Django
├── db/                    # Base de datos SQLite
├── static/                # Archivos estáticos
├── requirements.txt       # Dependencias Python
├── manage.py             # Script de gestión
└── .env.example         # Variables de entorno
```
