#!/bin/bash

# Script de limpieza y test completo para Jitsi Meet
# Limpia contenedores obsoletos y ejecuta tests individuales

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Limpieza y Test Completo de Jitsi Meet${NC}"
echo "=================================================="

# Función para imprimir mensajes
print_status() {
    local status="$1"
    local message="$2"
    
    case $status in
        "ERROR")
            echo -e "${RED}❌ ERROR:${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  WARNING:${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅ SUCCESS:${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO:${NC} $message"
            ;;
    esac
}

# 1. Limpiar contenedores obsoletos
print_status "INFO" "Limpiando contenedores obsoletos..."

# Detener todos los contenedores
docker compose down 2>/dev/null || true

# Eliminar contenedores obsoletos
docker container rm jitsi-meet 2>/dev/null || true
docker container rm jitsi-web 2>/dev/null || true
docker container rm jitsi-prosody 2>/dev/null || true
docker container rm jitsi-jicofo 2>/dev/null || true
docker container rm jitsi-jvb 2>/dev/null || true

print_status "SUCCESS" "Contenedores obsoletos eliminados"

# 2. Verificar configuración
print_status "INFO" "Verificando configuración..."

if [ ! -f ".env" ]; then
    print_status "WARNING" "Archivo .env no encontrado"
    if [ -f "env.example" ]; then
        print_status "INFO" "Copiando env.example a .env"
        cp env.example .env
    else
        print_status "ERROR" "Archivo env.example no encontrado"
        exit 1
    fi
fi

# 3. Generar contraseñas si es necesario
print_status "INFO" "Verificando contraseñas..."

if grep -q "JICOFO_COMPONENT_SECRET=$" .env || grep -q "JICOFO_AUTH_PASSWORD=$" .env || grep -q "JVB_AUTH_PASSWORD=$" .env; then
    print_status "WARNING" "Contraseñas vacías detectadas"
    if [ -f "gen-passwords.sh" ]; then
        print_status "INFO" "Generando contraseñas seguras..."
        bash gen-passwords.sh
    else
        print_status "ERROR" "Script gen-passwords.sh no encontrado"
        exit 1
    fi
else
    print_status "SUCCESS" "Contraseñas ya configuradas"
fi

# 4. Iniciar servicios
print_status "INFO" "Iniciando servicios de Jitsi Meet..."

docker compose up -d

if [ $? -eq 0 ]; then
    print_status "SUCCESS" "Servicios iniciados correctamente"
else
    print_status "ERROR" "Error al iniciar servicios"
    exit 1
fi

# 5. Esperar a que los servicios estén listos
print_status "INFO" "Esperando a que los servicios estén listos..."

sleep 10

# 6. Ejecutar tests con pytest
print_status "INFO" "Ejecutando tests con pytest..."

echo ""
echo -e "${BLUE}🧪 Ejecutando Tests con pytest${NC}"
echo "=================================="

# Ejecutar todos los tests con pytest
if ./run-tests.sh; then
    print_status "SUCCESS" "Todos los tests pasaron exitosamente"
else
    print_status "ERROR" "Algunos tests fallaron"
fi

# 7. Resumen final
echo ""
echo "=================================================="
echo -e "${BLUE}📊 RESUMEN FINAL${NC}"
echo "=================================================="

# Verificar estado de contenedores
echo ""
echo -e "${BLUE}Estado de contenedores:${NC}"
docker compose ps

echo ""
echo -e "${BLUE}Información de acceso:${NC}"
echo "🌐 URL principal: http://localhost:8080"
echo "🏠 Crear sala: http://localhost:8080/mi-sala"
echo "📊 Logs: docker compose logs -f"

echo ""
echo -e "${BLUE}Comandos útiles:${NC}"
echo "   Ver logs: docker compose logs -f"
echo "   Detener: docker compose down"
echo "   Reiniciar: docker compose restart"
echo "   Tests con pytest: ./run-tests.sh"
echo "   Tests específicos: ./run-tests.sh tests/test_web.py"

print_status "SUCCESS" "Limpieza y test completados"
echo ""
echo -e "${GREEN}🎉 ¡Jitsi Meet está listo para usar!${NC}"
