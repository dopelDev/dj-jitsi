# Django Jitsi - Estructura del Proyecto

## Estructura de Directorios

```
src/
├── config/                 # Configuración de Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── models/                 # Modelos de datos y migraciones
│   ├── __init__.py
│   ├── apps.py            # Configuración de app Django
│   ├── admin.py           # Configuración de admin
│   ├── models.py          # Modelos principales
│   ├── permissions.py     # Permisos y decoradores
│   └── migrations/        # Migraciones de base de datos
├── views/                  # Vistas y lógica de presentación
│   ├── __init__.py
│   ├── views.py           # Vistas principales
│   ├── urls.py            # URLs de la aplicación
│   ├── forms.py           # Formularios
│   └── context_processors.py  # Context processors
├── tests/                  # Tests del proyecto
│   ├── __init__.py
│   ├── tests.py           # Tests principales
│   └── conftest.py        # Configuración de pytest
├── utils/                  # Utilidades
│   ├── __init__.py
│   └── jitsi.py           # Utilidades de Jitsi
├── templates/              # Plantillas globales
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   └── ... (todas las plantillas)
├── pytest.ini            # Configuración de pytest
├── README.md              # Documentación
└── manage.py
```

## Organización

### Models (`models/`)
- **models.py**: Modelos principales (UserProfile, Meeting, SignupRequest)
- **permissions.py**: Decoradores y funciones de permisos

### Views (`views/`)
- **views.py**: Todas las vistas de la aplicación
- **urls.py**: Configuración de URLs
- **forms.py**: Formularios de Django
- **context_processors.py**: Context processors para templates

### Tests (`tests/`)
- **tests.py**: Tests completos para todos los endpoints
- **conftest.py**: Configuración de pytest

### Utils (`utils/`)
- **jitsi.py**: Utilidades para integración con Jitsi

## Ejecutar Tests

```bash
cd src
python -m pytest tests/ -v
```

## Ejecutar Servidor

```bash
cd src
python manage.py runserver
```
