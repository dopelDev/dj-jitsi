#!/bin/bash

# Wrapper para ejecutar test de WebSocket con Selenium
# Detecta el error: wss://http//localhost:8080/xmpp-websocket

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo -e "${BLUE}🧪 Test de WebSocket con Selenium${NC}"
echo "=================================================="

# 1. Verificar Python
print_status "INFO" "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_status "ERROR" "Python3 no encontrado. Instala Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_status "ERROR" "Python 3.8+ requerido. Versión actual: $PYTHON_VERSION"
    exit 1
fi

print_status "SUCCESS" "Python $PYTHON_VERSION encontrado"

# 2. Verificar pip
print_status "INFO" "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    print_status "ERROR" "pip3 no encontrado. Instala pip"
    exit 1
fi

print_status "SUCCESS" "pip3 encontrado"

# 3. Verificar/instalar dependencias
print_status "INFO" "Verificando dependencias de Python..."

# Verificar si existe entorno virtual
if [ -d "venv" ]; then
    print_status "INFO" "Entorno virtual encontrado, activando..."
    source venv/bin/activate
fi

# Instalar dependencias si es necesario
if ! python3 -c "import selenium" 2>/dev/null; then
    print_status "WARNING" "Selenium no encontrado, instalando dependencias..."
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip3 install selenium webdriver-manager python-dotenv requests
    fi
fi

print_status "SUCCESS" "Dependencias de Python verificadas"

# 4. Verificar que Jitsi esté ejecutándose
print_status "INFO" "Verificando que Jitsi esté ejecutándose..."

JITSI_URL=${JITSI_URL:-"http://localhost:8080"}

if ! curl -s -o /dev/null -w "%{http_code}" "$JITSI_URL" | grep -q "200"; then
    print_status "ERROR" "Jitsi no está accesible en $JITSI_URL"
    print_status "INFO" "Asegúrate de que los servicios estén ejecutándose:"
    print_status "INFO" "  docker compose up -d"
    exit 1
fi

print_status "SUCCESS" "Jitsi accesible en $JITSI_URL"

# 5. Verificar navegador
print_status "INFO" "Verificando navegador..."

BROWSER=${BROWSER:-"chrome"}

if [ "$BROWSER" = "chrome" ]; then
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
        print_status "WARNING" "Chrome/Chromium no encontrado, intentando con Firefox..."
        BROWSER="firefox"
    fi
fi

if [ "$BROWSER" = "firefox" ]; then
    if ! command -v firefox &> /dev/null; then
        print_status "ERROR" "Firefox no encontrado. Instala Chrome, Chromium o Firefox"
        exit 1
    fi
fi

print_status "SUCCESS" "Navegador $BROWSER disponible"

# 6. Configurar variables de entorno
print_status "INFO" "Configurando variables de entorno..."

# Cargar .env.test si existe
if [ -f ".env.test" ]; then
    print_status "INFO" "Cargando configuración desde .env.test"
    export $(grep -v '^#' .env.test | xargs)
fi

# Variables por defecto
export JITSI_URL=${JITSI_URL:-"http://localhost:8080"}
export TEST_ROOM=${TEST_ROOM:-"test-websocket-error"}
export HEADLESS=${HEADLESS:-"true"}
export TEST_TIMEOUT=${TEST_TIMEOUT:-"30"}
export BROWSER=${BROWSER:-"chrome"}
export SCREENSHOT_DIR=${SCREENSHOT_DIR:-"./test-results/screenshots"}
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}

print_status "SUCCESS" "Variables de entorno configuradas"

# 7. Crear directorios necesarios
print_status "INFO" "Creando directorios necesarios..."
mkdir -p test-results/screenshots
mkdir -p test-results

print_status "SUCCESS" "Directorios creados"

# 8. Ejecutar test de Python
print_status "INFO" "Ejecutando test de WebSocket con Selenium..."
echo ""

# Ejecutar el test de Python
if python3 test-websocket-selenium.py; then
    print_status "SUCCESS" "Test de WebSocket con Selenium: EXITOSO"
    echo ""
    echo -e "${GREEN}✅ No se detectaron errores de WebSocket${NC}"
    echo -e "${BLUE}📊 Revisa el reporte JSON en test-results/ para más detalles${NC}"
    exit 0
else
    print_status "ERROR" "Test de WebSocket con Selenium: FALLÓ"
    echo ""
    echo -e "${RED}❌ Se detectaron errores de WebSocket${NC}"
    echo -e "${BLUE}📊 Revisa el reporte JSON y screenshots en test-results/ para más detalles${NC}"
    exit 1
fi
