#!/bin/bash

# Script de Deploy para Jitsi Meet
# Despliega Jitsi Meet usando imagen oficial con configuración optimizada

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando deploy de Jitsi Meet...${NC}"

# Función para mostrar progreso
show_progress() {
    echo -e "${YELLOW}⏳ $1${NC}"
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar error
show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para verificar si Docker está ejecutándose
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        show_error "Docker no está ejecutándose. Por favor, inicia Docker primero."
        exit 1
    fi
    show_success "Docker está ejecutándose"
}

# Función para verificar puertos
check_ports() {
    show_progress "Verificando disponibilidad de puertos..."
    
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        show_error "Puerto 8080 ya está en uso. Por favor, libera el puerto o cambia la configuración."
        exit 1
    fi
    
    show_success "Puerto 8080 disponible"
}

# Función para crear directorios necesarios
create_directories() {
    show_progress "Creando directorios necesarios..."
    
    mkdir -p logs
    mkdir -p config/supervisor
    mkdir -p config/jitsi
    
    show_success "Directorios creados"
}

# Función para verificar archivos de configuración
check_config() {
    show_progress "Verificando archivos de configuración..."
    
    if [ ! -f "docker-compose.yml" ]; then
        show_error "Archivo docker-compose.yml no encontrado"
        exit 1
    fi
    
    if [ ! -f "env.example" ]; then
        show_warning "Archivo env.example no encontrado, creando uno básico..."
        cat > env.example << EOF
# Configuración de Jitsi Meet
JITSI_DOMAIN=localhost
PUBLIC_URL=http://localhost:8080
ENABLE_AUTH=false
ENABLE_GUESTS=1
ENABLE_WELCOME_PAGE=1
EOF
    fi
    
    show_success "Archivos de configuración verificados"
}

# Función para configurar variables de entorno
setup_env() {
    show_progress "Configurando variables de entorno..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            show_success "Archivo .env creado desde env.example"
        else
            show_warning "Creando archivo .env con configuración por defecto..."
            cat > .env << EOF
JITSI_DOMAIN=localhost
PUBLIC_URL=http://localhost:8080
ENABLE_AUTH=false
ENABLE_GUESTS=1
ENABLE_WELCOME_PAGE=1
EOF
        fi
    else
        show_success "Archivo .env ya existe"
    fi
}

# Función para descargar imagen oficial
pull_image() {
    show_progress "Descargando imagen oficial de Jitsi..."
    
    docker pull jitsi/web:stable
    show_success "Imagen oficial descargada"
}

# Función para desplegar servicios
deploy_services() {
    show_progress "Desplegando servicios de Jitsi..."
    
    docker compose up -d
    show_success "Servicios desplegados"
}

# Función para verificar el estado
check_status() {
    show_progress "Verificando estado de los servicios..."
    
    sleep 5  # Esperar a que los servicios se inicien
    
    if docker compose ps | grep -q "Up"; then
        show_success "Servicios ejecutándose correctamente"
    else
        show_error "Error al iniciar los servicios"
        docker compose logs
        exit 1
    fi
}

# Función para mostrar información de acceso
show_access_info() {
    echo -e "${GREEN}🎉 Deploy completado exitosamente!${NC}"
    echo ""
    echo -e "${BLUE}📊 Información de acceso:${NC}"
    echo -e "• URL: ${GREEN}http://localhost:8080${NC}"
    echo -e "• Imagen: ${GREEN}jitsi/web:stable${NC}"
    echo -e "• Estado: ${GREEN}Ejecutándose${NC}"
    echo ""
    echo -e "${BLUE}📝 Comandos útiles:${NC}"
    echo -e "• Ver logs: ${YELLOW}docker compose logs -f${NC}"
    echo -e "• Detener: ${YELLOW}docker compose down${NC}"
    echo -e "• Reiniciar: ${YELLOW}docker compose restart${NC}"
    echo -e "• Cleanup: ${YELLOW}./cleanup.sh${NC}"
    echo ""
    echo -e "${BLUE}🔍 Verificando conectividad...${NC}"
    
    # Verificar que el servicio esté respondiendo
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
        show_success "Jitsi Meet está respondiendo correctamente"
    else
        show_warning "Jitsi Meet puede estar iniciándose, espera unos segundos más"
    fi
}

# Ejecutar funciones en orden
main() {
    check_docker
    check_ports
    create_directories
    check_config
    setup_env
    pull_image
    deploy_services
    check_status
    show_access_info
}

# Ejecutar script principal
main "$@"
