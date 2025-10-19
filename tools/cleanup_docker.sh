#!/bin/bash
# Script para limpiar completamente el entorno Docker de django-jitsi
# Elimina contenedores, volúmenes, redes e imágenes del proyecto

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Limpiando entorno Docker de django-jitsi ===${NC}"

# Función para mostrar mensajes con colores
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    log_error "Docker no está corriendo. Por favor, inicia Docker primero."
    exit 1
fi

log_info "Deteniendo y eliminando contenedores del proyecto..."

# Detener contenedores del proyecto si están corriendo
if docker compose ps | grep -q "Up"; then
    log_info "Deteniendo contenedores..."
    docker compose down
    log_success "Contenedores detenidos"
else
    log_info "No hay contenedores corriendo"
fi

# Eliminar contenedores del proyecto (incluso si están parados)
log_info "Eliminando contenedores del proyecto..."
docker compose down --remove-orphans --volumes 2>/dev/null || true

# Buscar y eliminar contenedores relacionados con el proyecto
PROJECT_CONTAINERS=$(docker ps -a --filter "name=jitsi-django" --format "{{.Names}}" 2>/dev/null || true)
if [ ! -z "$PROJECT_CONTAINERS" ]; then
    log_info "Eliminando contenedores relacionados..."
    echo "$PROJECT_CONTAINERS" | xargs docker rm -f 2>/dev/null || true
    log_success "Contenedores relacionados eliminados"
fi

# Eliminar volúmenes del proyecto
log_info "Eliminando volúmenes del proyecto..."
VOLUMES=$(docker volume ls --filter "name=jitsi-django" --format "{{.Name}}" 2>/dev/null || true)
if [ ! -z "$VOLUMES" ]; then
    echo "$VOLUMES" | xargs docker volume rm -f 2>/dev/null || true
    log_success "Volúmenes eliminados"
else
    log_info "No se encontraron volúmenes del proyecto"
fi

# Eliminar volúmenes huérfanos
log_info "Eliminando volúmenes huérfanos..."
ORPHAN_VOLUMES=$(docker volume ls -q -f dangling=true 2>/dev/null || true)
if [ ! -z "$ORPHAN_VOLUMES" ]; then
    echo "$ORPHAN_VOLUMES" | xargs docker volume rm -f 2>/dev/null || true
    log_success "Volúmenes huérfanos eliminados"
fi

# Eliminar redes del proyecto
log_info "Eliminando redes del proyecto..."
NETWORKS=$(docker network ls --filter "name=jitsi-django" --format "{{.Name}}" 2>/dev/null || true)
if [ ! -z "$NETWORKS" ]; then
    echo "$NETWORKS" | xargs docker network rm 2>/dev/null || true
    log_success "Redes eliminadas"
fi

# Eliminar imágenes del proyecto
log_info "Eliminando imágenes del proyecto..."
PROJECT_IMAGES=$(docker images --filter "reference=jitsi-django*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
if [ ! -z "$PROJECT_IMAGES" ]; then
    echo "$PROJECT_IMAGES" | xargs docker rmi -f 2>/dev/null || true
    log_success "Imágenes del proyecto eliminadas"
fi

# Limpiar directorio de base de datos local
log_info "Limpiando directorio de base de datos local..."
if [ -d "db" ]; then
    rm -rf db/*
    log_success "Directorio de base de datos limpiado"
fi

# Limpiar archivos temporales de Docker
log_info "Limpiando archivos temporales de Docker..."
docker system prune -f --volumes 2>/dev/null || true
log_success "Archivos temporales eliminados"

# Mostrar resumen de limpieza
echo ""
echo -e "${GREEN}=== Resumen de limpieza ===${NC}"
echo -e "${GREEN}✓ Contenedores eliminados${NC}"
echo -e "${GREEN}✓ Volúmenes eliminados${NC}"
echo -e "${GREEN}✓ Redes eliminadas${NC}"
echo -e "${GREEN}✓ Imágenes del proyecto eliminadas${NC}"
echo -e "${GREEN}✓ Directorio de base de datos limpiado${NC}"
echo -e "${GREEN}✓ Archivos temporales eliminados${NC}"

echo ""
log_success "Limpieza completa del entorno Docker finalizada"
echo ""
echo -e "${YELLOW}Para recrear el entorno, ejecuta:${NC}"
echo -e "${BLUE}  ./test_setup.sh${NC}"
echo ""
echo -e "${YELLOW}Para solo construir las imágenes:${NC}"
echo -e "${BLUE}  docker compose build${NC}"
