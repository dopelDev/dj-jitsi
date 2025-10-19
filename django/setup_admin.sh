#!/bin/bash

# Cargar variables de entorno desde env_simple
source env_simple

# Activar entorno virtual
source venv/bin/activate

# Ir al directorio src
cd src

# Ejecutar comando para crear admin desde variables de entorno
python manage.py create_admin_from_env

echo "Setup de admin completado"
