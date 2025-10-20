#!/bin/bash

# Script de Cleanup para Jitsi Meet
# Limpia contenedores, imágenes, volúmenes y archivos temporales

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Iniciando cleanup de Jitsi Meet...${NC}"

# Función para mostrar progreso
show_progress() {
    echo -e "${YELLOW}⏳ $1${NC}"
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar advertencia
show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Detener y eliminar contenedores
show_progress "Deteniendo contenedores de Jitsi..."
if docker compose ps -q | grep -q .; then
    docker compose down --remove-orphans
    show_success "Contenedores detenidos y eliminados"
else
    echo "No hay contenedores de Jitsi ejecutándose"
fi

# 2. Eliminar imágenes de Jitsi
show_progress "Eliminando imágenes de Jitsi..."
if docker images | grep -q jitsi; then
    docker images | grep jitsi | awk '{print $3}' | xargs -r docker rmi -f
    show_success "Imágenes de Jitsi eliminadas"
else
    echo "No hay imágenes de Jitsi para eliminar"
fi

# 3. Limpiar volúmenes huérfanos
show_progress "Limpiando volúmenes huérfanos..."
docker volume prune -f
show_success "Volúmenes huérfanos eliminados"

# 4. Limpiar redes no utilizadas
show_progress "Limpiando redes no utilizadas..."
docker network prune -f
show_success "Redes no utilizadas eliminadas"

# 5. Limpiar archivos temporales
show_progress "Limpiando archivos temporales..."
if [ -d "logs" ]; then
    rm -rf logs/*
    show_success "Logs limpiados"
fi

if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache
    show_success "Cache de pytest eliminado"
fi

if [ -d "test-results" ]; then
    rm -rf test-results
    show_success "Resultados de tests eliminados"
fi

# 6. Limpiar archivos de configuración temporal
show_progress "Limpiando archivos de configuración temporal..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
show_success "Archivos temporales eliminados"

# 7. Limpiar cache de Docker
show_progress "Limpiando cache de Docker..."
docker system prune -f
show_success "Cache de Docker limpiado"

# 8. Mostrar espacio liberado
show_progress "Verificando espacio liberado..."
echo -e "${BLUE}📊 Espacio en disco después del cleanup:${NC}"
df -h . | tail -1

echo -e "${GREEN}🎉 Cleanup completado exitosamente!${NC}"
echo -e "${BLUE}💡 Para volver a desplegar, ejecuta: ./deploy.sh${NC}"
