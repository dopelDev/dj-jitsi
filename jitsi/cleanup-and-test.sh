#!/bin/bash

# Script de limpieza y test completo para Jitsi Meet
# Limpia contenedores obsoletos y ejecuta tests individuales usando venv

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

# Verificar y activar entorno virtual
print_status "INFO" "Verificando entorno virtual..."

# Buscar el venv en diferentes ubicaciones posibles
VENV_PATHS=(
    "./venv"
    "../venv" 
    "./jitsi/venv"
    "../jitsi/venv"
    "./tests/venv"
)

VENV_FOUND=""
for venv_path in "${VENV_PATHS[@]}"; do
    if [ -d "$venv_path" ] && [ -f "$venv_path/bin/activate" ]; then
        VENV_FOUND="$venv_path"
        break
    fi
done

if [ -n "$VENV_FOUND" ]; then
    print_status "SUCCESS" "Entorno virtual encontrado en: $VENV_FOUND"
    print_status "INFO" "Activando entorno virtual..."
    source "$VENV_FOUND/bin/activate"
    
    # Verificar que el venv está activo
    if [ -n "$VIRTUAL_ENV" ]; then
        print_status "SUCCESS" "Entorno virtual activado: $VIRTUAL_ENV"
        print_status "INFO" "Python: $(python --version 2>/dev/null || echo 'No encontrado')"
        print_status "INFO" "pip: $(pip --version 2>/dev/null || echo 'No encontrado')"
        
        # Verificar dependencias críticas
        print_status "INFO" "Verificando dependencias críticas..."
        if python -c "import pytest" 2>/dev/null; then
            print_status "SUCCESS" "pytest disponible"
        else
            print_status "WARNING" "pytest no encontrado - instalando..."
            pip install pytest pytest-html pytest-xdist || print_status "ERROR" "No se pudo instalar pytest"
        fi
        
        if python -c "import docker" 2>/dev/null; then
            print_status "SUCCESS" "docker-py disponible"
        else
            print_status "WARNING" "docker-py no encontrado - instalando..."
            pip install docker || print_status "ERROR" "No se pudo instalar docker-py"
        fi
        
        if python -c "import requests" 2>/dev/null; then
            print_status "SUCCESS" "requests disponible"
        else
            print_status "WARNING" "requests no encontrado - instalando..."
            pip install requests || print_status "ERROR" "No se pudo instalar requests"
        fi
    else
        print_status "WARNING" "No se pudo activar el entorno virtual"
    fi
else
    print_status "WARNING" "No se encontró entorno virtual - usando Python del sistema"
    print_status "INFO" "Python del sistema: $(python3 --version 2>/dev/null || echo 'No encontrado')"
fi

# Función para obtener el comando de Python correcto
get_python_cmd() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "python"
    else
        echo "python3"
    fi
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

# 6. Verificar estado de servicios antes de tests
print_status "INFO" "Verificando estado de servicios..."

echo ""
echo -e "${BLUE}🔍 Verificación de Servicios${NC}"
echo "=================================="

# Verificar contenedores
print_status "INFO" "Estado de contenedores:"
docker compose ps

echo ""
print_status "INFO" "Verificando conectividad de servicios..."

# Verificar web
if curl -s -f http://localhost:8080 > /dev/null 2>&1; then
    print_status "SUCCESS" "Web (puerto 8080) - ✅ Accesible"
else
    print_status "WARNING" "Web (puerto 8080) - ❌ No accesible"
fi

# Verificar prosody
if curl -s -f http://localhost:5280/http-bind/ > /dev/null 2>&1; then
    print_status "SUCCESS" "Prosody (puerto 5280) - ✅ Accesible"
else
    print_status "WARNING" "Prosody (puerto 5280) - ❌ No accesible"
fi

# Verificar puerto UDP de JVB
if netstat -tuln 2>/dev/null | grep -q ":10000"; then
    print_status "SUCCESS" "JVB (puerto 10000 UDP) - ✅ Escuchando"
else
    print_status "WARNING" "JVB (puerto 10000 UDP) - ❌ No escuchando"
fi

echo ""

# 7. Ejecutar tests con pytest
print_status "INFO" "Ejecutando tests con pytest..."

echo ""
echo -e "${BLUE}🧪 Ejecutando Tests con pytest${NC}"
echo "=================================="

# Mostrar información de configuración de tests
PYTHON_CMD=$(get_python_cmd)
print_status "INFO" "Configuración de tests:"
echo "📁 Directorio de tests: $(pwd)/tests"
echo "🐍 Python: $($PYTHON_CMD --version 2>/dev/null || echo 'No encontrado')"
echo "📦 pytest: $($PYTHON_CMD -m pytest --version 2>/dev/null || echo 'No encontrado')"
echo "🐳 Docker: $(docker --version 2>/dev/null || echo 'No encontrado')"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🔧 Entorno virtual: $VIRTUAL_ENV"
fi

echo ""
print_status "INFO" "Ejecutando tests individuales con información detallada..."

# Ejecutar tests con información detallada
if $PYTHON_CMD -m pytest tests/ -v --tb=short --durations=10; then
    print_status "SUCCESS" "Todos los tests pasaron exitosamente"
    TEST_RESULT="SUCCESS"
else
    print_status "WARNING" "Algunos tests fallaron - revisando detalles..."
    TEST_RESULT="FAILED"
    
    echo ""
    print_status "INFO" "Ejecutando tests específicos para diagnóstico..."
    
    # Tests específicos para diagnóstico
    echo ""
    echo -e "${YELLOW}🔍 Diagnóstico de Tests Específicos${NC}"
    echo "=================================="
    
    # Test de contenedores
    print_status "INFO" "Verificando tests de contenedores..."
    $PYTHON_CMD -m pytest tests/test_jicofo.py::test_jicofo_container_running -v -s || true
    $PYTHON_CMD -m pytest tests/test_jvb.py::test_jvb_container_running -v -s || true
    $PYTHON_CMD -m pytest tests/test_prosody.py::test_prosody_container_running -v -s || true
    $PYTHON_CMD -m pytest tests/test_web.py::test_web_container_running -v -s || true
    
    # Test de procesos
    print_status "INFO" "Verificando tests de procesos..."
    $PYTHON_CMD -m pytest tests/test_jicofo.py::test_jicofo_process_running -v -s || true
    $PYTHON_CMD -m pytest tests/test_jvb.py::test_jvb_process_running -v -s || true
    $PYTHON_CMD -m pytest tests/test_prosody.py::test_prosody_xmpp_connection -v -s || true
    $PYTHON_CMD -m pytest tests/test_web.py::test_web_nginx_process -v -s || true
    
    # Test de configuración
    print_status "INFO" "Verificando tests de configuración..."
    $PYTHON_CMD -m pytest tests/test_prosody.py::test_prosody_configuration_files -v -s || true
fi

# 8. Resumen final con información detallada
echo ""
echo "=================================================="
echo -e "${BLUE}📊 RESUMEN FINAL${NC}"
echo "=================================================="

# Mostrar resultado de tests
echo ""
if [ "$TEST_RESULT" = "SUCCESS" ]; then
    print_status "SUCCESS" "✅ TODOS LOS TESTS PASARON EXITOSAMENTE"
    echo -e "${GREEN}🎉 ¡Jitsi Meet está funcionando correctamente!${NC}"
else
    print_status "WARNING" "⚠️  ALGUNOS TESTS FALLARON - Revisar detalles arriba"
    echo -e "${YELLOW}🔧 Se recomienda revisar la configuración${NC}"
fi

# Verificar estado de contenedores
echo ""
echo -e "${BLUE}📋 Estado de contenedores:${NC}"
docker compose ps

# Mostrar información de salud de contenedores
echo ""
echo -e "${BLUE}🏥 Salud de contenedores:${NC}"
for container in jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb; do
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container"; then
        status=$(docker ps --format "{{.Status}}" --filter "name=$container")
        if echo "$status" | grep -q "healthy\|Up"; then
            print_status "SUCCESS" "$container: $status"
        else
            print_status "WARNING" "$container: $status"
        fi
    else
        print_status "ERROR" "$container: No está ejecutándose"
    fi
done

# Mostrar logs recientes si hay problemas
if [ "$TEST_RESULT" = "FAILED" ]; then
    echo ""
    echo -e "${YELLOW}📋 Logs recientes de contenedores (últimas 5 líneas):${NC}"
    for container in jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb; do
        if docker ps --format "{{.Names}}" | grep -q "$container"; then
            echo ""
            echo -e "${BLUE}📄 Logs de $container:${NC}"
            docker logs --tail=5 "$container" 2>/dev/null || echo "No se pudieron obtener logs"
        fi
    done
fi

echo ""
echo -e "${BLUE}🌐 Información de acceso:${NC}"
echo "   🏠 URL principal: http://localhost:8080"
echo "   🎯 Crear sala: http://localhost:8080/mi-sala"
echo "   📊 BOSH endpoint: http://localhost:5280/http-bind/"
echo "   🔌 WebSocket: ws://localhost:5280/xmpp-websocket"

echo ""
echo -e "${BLUE}🛠️  Comandos útiles:${NC}"
echo "   📋 Ver logs: docker compose logs -f"
echo "   🛑 Detener: docker compose down"
echo "   🔄 Reiniciar: docker compose restart"
echo "   🧪 Tests: ./run-tests.sh"
echo "   🔍 Tests específicos: $PYTHON_CMD -m pytest tests/test_web.py -v -s"
echo "   🐳 Entrar a contenedor: docker exec -it jitsi-web bash"

echo ""
echo -e "${BLUE}📊 Estadísticas de tests:${NC}"
if [ -f "test-results/junit.xml" ]; then
    echo "   📄 Reporte XML: test-results/junit.xml"
fi
if [ -f "test-results/report.html" ]; then
    echo "   🌐 Reporte HTML: test-results/report.html"
fi

# Mostrar información de configuración
echo ""
echo -e "${BLUE}⚙️  Configuración actual:${NC}"
echo "   📁 Directorio: $(pwd)"
echo "   🐍 Python: $($PYTHON_CMD --version 2>/dev/null || echo 'No encontrado')"
echo "   🐳 Docker: $(docker --version 2>/dev/null || echo 'No encontrado')"
echo "   📦 Docker Compose: $(docker compose version 2>/dev/null || echo 'No encontrado')"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "   🔧 Entorno virtual: $VIRTUAL_ENV"
    echo "   📦 Paquetes instalados: $(pip list --format=freeze | wc -l) paquetes"
fi

print_status "SUCCESS" "Limpieza y test completados"
echo ""
if [ "$TEST_RESULT" = "SUCCESS" ]; then
    echo -e "${GREEN}🎉 ¡Jitsi Meet está listo para usar!${NC}"
else
    echo -e "${YELLOW}⚠️  Revisar configuración y logs para resolver problemas${NC}"
fi
