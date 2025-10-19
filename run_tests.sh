#!/bin/bash
# Script para ejecutar tests con pytest

set -e

echo "=== Ejecutando tests de Django-Jitsi ==="

# Verificar que Docker esté corriendo
if ! docker compose ps | grep -q "web"; then
    echo "Iniciando contenedor para tests..."
    docker compose up -d
    sleep 5
fi

echo "=== Ejecutando migraciones ==="
docker compose exec web python manage.py migrate

echo "=== Ejecutando tests con pytest ==="
docker compose exec web python -m pytest src/accounts/tests.py -v

echo "=== Ejecutando tests con Django test runner ==="
docker compose exec web python manage.py test accounts.tests

echo "=== Tests completados exitosamente ==="

# Opcional: mantener contenedor corriendo
# docker compose down
