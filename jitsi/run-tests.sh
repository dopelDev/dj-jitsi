#!/bin/bash
# Wrapper para ejecutar tests de Python con pytest

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status="$1"
    local message="$2"
    case $status in
        "ERROR") echo -e "${RED}❌ ERROR:${NC} $message"; exit 1 ;;
        "SUCCESS") echo -e "${GREEN}✅ SUCCESS:${NC} $message" ;;
        "INFO") echo -e "${BLUE}ℹ️  INFO:${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}⚠️  WARNING:${NC} $message" ;;
    esac
}

echo -e "${BLUE}🧪 Ejecutando Tests de Jitsi Meet con pytest${NC}"
echo "============================================="

# 1. Verificar Python
print_status "INFO" "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_status "ERROR" "Python3 no encontrado. Instala Python 3.8+"
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "SUCCESS" "Python $PYTHON_VERSION encontrado"

# 2. Verificar pip
print_status "INFO" "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    print_status "ERROR" "pip3 no encontrado. Instala pip para Python 3."
fi
print_status "SUCCESS" "pip3 encontrado"

# 3. Configurar entorno virtual
print_status "INFO" "Verificando entorno virtual..."
if [ ! -d "venv" ]; then
    print_status "INFO" "Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_status "ERROR" "Fallo al crear entorno virtual."
    fi
fi

source venv/bin/activate
if [ $? -ne 0 ]; then
    print_status "ERROR" "Fallo al activar entorno virtual."
fi

# 4. Instalar dependencias
print_status "INFO" "Instalando dependencias de Python..."
pip install -r tests/requirements.txt
if [ $? -ne 0 ]; then
    print_status "ERROR" "Fallo al instalar dependencias de Python."
fi
print_status "SUCCESS" "Dependencias de Python instaladas"

# 5. Verificar que Jitsi esté ejecutándose
print_status "INFO" "Verificando que Jitsi esté ejecutándose..."
JITSI_URL=$(grep -E '^PUBLIC_URL=' .env | cut -d'=' -f2)
if [ -z "$JITSI_URL" ]; then
    JITSI_URL="http://localhost:8080"
fi

if curl -s -o /dev/null -w "%{http_code}" "$JITSI_URL" | grep -q "200"; then
    print_status "SUCCESS" "Jitsi accesible en $JITSI_URL"
else
    print_status "WARNING" "Jitsi no accesible en $JITSI_URL. Algunos tests pueden fallar."
fi

# 6. Crear directorio de resultados
mkdir -p test-results

# 7. Ejecutar pytest
print_status "INFO" "Ejecutando tests con pytest..."
python3 tests/run_tests.py "$@"

if [ $? -eq 0 ]; then
    print_status "SUCCESS" "Todos los tests pasaron exitosamente"
    echo ""
    echo -e "${GREEN}📊 Reportes generados:${NC}"
    echo "   - HTML: test-results/report.html"
    echo "   - JUnit: test-results/junit.xml"
    echo ""
    echo -e "${GREEN}🎉 ¡Tests completados exitosamente!${NC}"
else
    print_status "ERROR" "Algunos tests fallaron. Revisa los reportes en test-results/"
fi

deactivate
