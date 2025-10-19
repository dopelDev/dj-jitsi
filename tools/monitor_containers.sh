#!/bin/bash
# Script para monitorear contenedores de django-jitsi

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Monitor de Contenedores Django-Jitsi ===${NC}"

# Función para mostrar estado de contenedores
show_container_status() {
    echo -e "${BLUE}=== Estado de Contenedores ===${NC}"
    
    if docker compose ps | grep -q "Up"; then
        echo -e "${GREEN}✓ Contenedores corriendo:${NC}"
        docker compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}\t{{.Status}}"
    else
        echo -e "${RED}✗ No hay contenedores corriendo${NC}"
        docker compose ps
    fi
}

# Función para mostrar logs recientes
show_recent_logs() {
    echo ""
    echo -e "${BLUE}=== Logs Recientes (últimas 20 líneas) ===${NC}"
    
    if docker compose ps | grep -q "Up"; then
        docker compose logs --tail=20 web
    else
        echo -e "${YELLOW}[WARNING]${NC} No se pueden mostrar logs (contenedor no corriendo)"
    fi
}

# Función para mostrar uso de recursos
show_resource_usage() {
    echo ""
    echo -e "${BLUE}=== Uso de Recursos ===${NC}"
    
    if docker compose ps | grep -q "Up"; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    else
        echo -e "${YELLOW}[WARNING]${NC} No se pueden mostrar estadísticas (contenedor no corriendo)"
    fi
}

# Función para mostrar estado de la base de datos
show_database_status() {
    echo ""
    echo -e "${BLUE}=== Estado de Base de Datos ===${NC}"
    
    if [ -f "db/db.sqlite3" ]; then
        DB_SIZE=$(du -h "db/db.sqlite3" | cut -f1)
        DB_DATE=$(stat -c %y "db/db.sqlite3" | cut -d' ' -f1)
        echo -e "${GREEN}✓ Base de datos encontrada${NC}"
        echo "  Tamaño: $DB_SIZE"
        echo "  Última modificación: $DB_DATE"
        
        # Verificar conexión a la base de datos si el contenedor está corriendo
        if docker compose ps | grep -q "Up"; then
            echo ""
            echo -e "${BLUE}=== Estadísticas de la Base de Datos ===${NC}"
            docker compose exec web python manage.py shell -c "
from accounts.models import SignupRequest, Meeting
from django.contrib.auth.models import User
print(f'Usuarios: {User.objects.count()}')
print(f'Solicitudes: {SignupRequest.objects.count()}')
print(f'  - Pendientes: {SignupRequest.objects.filter(status=\"pending\").count()}')
print(f'  - Aprobadas: {SignupRequest.objects.filter(status=\"approved\").count()}')
print(f'  - Rechazadas: {SignupRequest.objects.filter(status=\"rejected\").count()}')
print(f'Reuniones: {Meeting.objects.count()}')
"
        fi
    else
        echo -e "${YELLOW}⚠ Base de datos no encontrada${NC}"
    fi
}

# Función para mostrar estado de la aplicación web
show_web_status() {
    echo ""
    echo -e "${BLUE}=== Estado de la Aplicación Web ===${NC}"
    
    if docker compose ps | grep -q "Up"; then
        # Verificar si la aplicación responde
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200\|302"; then
            echo -e "${GREEN}✓ Aplicación web respondiendo${NC}"
            echo "  URL: http://localhost:8000"
            echo "  Admin: http://localhost:8000/admin"
        else
            echo -e "${YELLOW}⚠ Aplicación web no responde correctamente${NC}"
        fi
    else
        echo -e "${RED}✗ Aplicación web no disponible (contenedor no corriendo)${NC}"
    fi
}

# Función principal de monitoreo
main_monitor() {
    show_container_status
    show_recent_logs
    show_resource_usage
    show_database_status
    show_web_status
    
    echo ""
    echo -e "${BLUE}=== Comandos Útiles ===${NC}"
    echo "Para ver logs en tiempo real: docker compose logs -f"
    echo "Para reiniciar contenedores: docker compose restart"
    echo "Para detener contenedores: docker compose down"
    echo "Para iniciar contenedores: docker compose up -d"
}

# Función de monitoreo continuo
continuous_monitor() {
    echo -e "${BLUE únete al monitoreo continuo (presiona Ctrl+C para salir)${NC}"
    echo ""
    
    while true; do
        clear
        main_monitor
        echo ""
        echo -e "${YELLOW}Actualizando en 10 segundos... (Ctrl+C para salir)${NC}"
        sleep 10
    done
}

# Verificar argumentos
if [ "$1" = "--continuous" ] || [ "$1" = "-c" ]; then
    continuous_monitor
else
    main_monitor
fi
