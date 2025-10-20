#!/bin/bash

# Script de validación para Jitsi Meet
# Verifica configuración antes y después del despliegue

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
ERRORS=0
WARNINGS=0
SUCCESS=0

# Función para imprimir mensajes
print_status() {
    local status="$1"
    local message="$2"
    
    case $status in
        "ERROR")
            echo -e "${RED}❌ ERROR:${NC} $message"
            ((ERRORS++))
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  WARNING:${NC} $message"
            ((WARNINGS++))
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅ SUCCESS:${NC} $message"
            ((SUCCESS++))
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO:${NC} $message"
            ;;
    esac
}

# Función para verificar archivo
check_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        print_status "SUCCESS" "$description existe: $file"
        return 0
    else
        print_status "ERROR" "$description no encontrado: $file"
        return 1
    fi
}

# Función para verificar variable en .env
check_env_var() {
    local var_name="$1"
    local description="$2"
    local required="${3:-true}"
    
    if [ -f ".env" ]; then
        if grep -q "^${var_name}=" .env; then
            local value=$(grep "^${var_name}=" .env | cut -d'=' -f2)
            if [ -n "$value" ] && [ "$value" != "" ]; then
                print_status "SUCCESS" "$description configurado: $var_name"
                return 0
            else
                if [ "$required" = "true" ]; then
                    print_status "ERROR" "$description está vacío: $var_name"
                    return 1
                else
                    print_status "WARNING" "$description está vacío: $var_name (opcional)"
                    return 0
                fi
            fi
        else
            if [ "$required" = "true" ]; then
                print_status "ERROR" "$description no encontrado: $var_name"
                return 1
            else
                print_status "WARNING" "$description no encontrado: $var_name (opcional)"
                return 0
            fi
        fi
    else
        print_status "ERROR" "Archivo .env no existe"
        return 1
    fi
}

# Función para verificar contenedores
check_container() {
    local container="$1"
    local description="$2"
    
    if docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep -q "$container.*Up"; then
        print_status "SUCCESS" "$description ejecutándose: $container"
        return 0
    else
        print_status "ERROR" "$description no está ejecutándose: $container"
        return 1
    fi
}

# Función para verificar logs
check_logs() {
    local service="$1"
    local pattern="$2"
    local description="$3"
    
    if docker compose logs "$service" 2>/dev/null | grep -q "$pattern"; then
        print_status "SUCCESS" "$description en $service"
        return 0
    else
        print_status "WARNING" "$description no encontrado en $service"
        return 1
    fi
}

echo -e "${BLUE}🔍 Validando configuración de Jitsi Meet...${NC}"
echo "=================================================="

# Verificar archivos necesarios
print_status "INFO" "Verificando archivos necesarios..."

check_file "env.example" "Archivo de plantilla de variables"
check_file "gen-passwords.sh" "Script de generación de contraseñas"
check_file "docker-compose.yml" "Configuración de Docker Compose"
check_file ".env" "Archivo de variables de entorno"

# Verificar permisos de ejecución
if [ -f "gen-passwords.sh" ]; then
    if [ -x "gen-passwords.sh" ]; then
        print_status "SUCCESS" "gen-passwords.sh tiene permisos de ejecución"
    else
        print_status "WARNING" "gen-passwords.sh no tiene permisos de ejecución"
        chmod +x gen-passwords.sh
        print_status "INFO" "Permisos de ejecución agregados a gen-passwords.sh"
    fi
fi

echo ""
print_status "INFO" "Verificando variables de entorno críticas..."

# Verificar variables críticas
check_env_var "JICOFO_COMPONENT_SECRET" "Secreto del componente Jicofo"
check_env_var "JICOFO_AUTH_PASSWORD" "Contraseña del usuario focus"
check_env_var "JVB_AUTH_PASSWORD" "Contraseña del usuario jvb"
check_env_var "XMPP_DOMAIN" "Dominio XMPP principal"
check_env_var "XMPP_AUTH_DOMAIN" "Dominio XMPP de autenticación"

# Verificar variables opcionales
check_env_var "JITSI_DOMAIN" "Dominio público de Jitsi" "false"
check_env_var "PUBLIC_URL" "URL pública de acceso" "false"

echo ""
print_status "INFO" "Verificando estado de contenedores..."

# Verificar si Docker está ejecutándose
if ! docker info >/dev/null 2>&1; then
    print_status "ERROR" "Docker no está ejecutándose"
    echo ""
    echo -e "${RED}❌ RESUMEN: Docker no está disponible${NC}"
    exit 1
fi

# Verificar contenedores si están ejecutándose
if docker compose ps --format "table {{.Name}}" | grep -q "jitsi"; then
    print_status "INFO" "Contenedores de Jitsi detectados, verificando estado..."
    
    check_container "jitsi-prosody" "Servidor XMPP (Prosody)"
    check_container "jitsi-jicofo" "Conference Focus (Jicofo)"
    check_container "jitsi-jvb" "Videobridge (JVB)"
    check_container "jitsi-web" "Frontend Web"
    
    echo ""
    print_status "INFO" "Verificando logs de servicios..."
    
    # Verificar logs de Prosody
    if docker compose logs prosody 2>/dev/null | grep -qi "fatal\|error"; then
        print_status "ERROR" "Errores FATAL detectados en Prosody"
        docker compose logs prosody | grep -i "fatal\|error" | head -5
    else
        print_status "SUCCESS" "Prosody sin errores FATAL"
    fi
    
    # Verificar conexión de Jicofo
    check_logs "jicofo" "Connected to XMPP" "Conexión XMPP exitosa"
    check_logs "jicofo" "Focus role: authorized" "Autorización de Focus"
    
    # Verificar conexión de JVB
    check_logs "jvb" "Connected to XMPP" "Conexión XMPP exitosa"
    check_logs "jvb" "Joined MUC" "Unión a sala MUC"
    
else
    print_status "INFO" "Contenedores no están ejecutándose"
    print_status "INFO" "Para iniciar: docker compose up -d"
fi

echo ""
echo "=================================================="
echo -e "${BLUE}📊 RESUMEN DE VALIDACIÓN${NC}"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ ERRORES: $ERRORS${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIAS: $WARNINGS${NC}"
fi

if [ $SUCCESS -gt 0 ]; then
    echo -e "${GREEN}✅ ÉXITOS: $SUCCESS${NC}"
fi

echo ""

# Determinar estado final
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ CONFIGURACIÓN INCOMPLETA${NC}"
    echo ""
    echo "Acciones recomendadas:"
    echo "1. Ejecutar: bash gen-passwords.sh"
    echo "2. Verificar archivo .env"
    echo "3. Revisar logs: docker compose logs"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  CONFIGURACIÓN PARCIAL${NC}"
    echo ""
    echo "Revisa las advertencias arriba para optimizar la configuración."
    exit 0
else
    echo -e "${GREEN}✅ CONFIGURACIÓN CORRECTA${NC}"
    echo ""
    echo "¡Todo está configurado correctamente!"
    echo "Puedes acceder a Jitsi en: http://localhost:8080"
    exit 0
fi
