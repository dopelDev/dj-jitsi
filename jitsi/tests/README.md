# Tests de Jitsi Meet con pytest

Este directorio contiene tests automatizados para verificar el funcionamiento correcto de todos los componentes de Jitsi Meet, implementados en Python con pytest.

## 🧪 Estructura de Tests

### Tests por Componente

- **`test_prosody.py`** - Tests del servidor XMPP (Prosody)
- **`test_jicofo.py`** - Tests del componente de enfoque (Jicofo)
- **`test_jvb.py`** - Tests del puente de video (JVB)
- **`test_web.py`** - Tests del frontend web
- **`test_websocket.py`** - Tests de conectividad WebSocket
- **`test_websocket_url.py`** - Tests de validación de URLs WebSocket
- **`test_websocket_error_specific.py`** - Test del error específico reportado
- **`test_websocket_selenium.py`** - Tests con Selenium para detección en navegador

### Archivos de Configuración

- **`conftest.py`** - Fixtures comunes para todos los tests
- **`pytest.ini`** - Configuración de pytest
- **`requirements.txt`** - Dependencias de Python
- **`run_tests.py`** - Script principal para ejecutar tests
- **`env.test`** - Variables de entorno para tests

## 🚀 Instalación y Configuración

### Requisitos

- Python 3.8+
- pytest
- Docker (para tests de integración)
- Chrome/Firefox (para tests de Selenium)

### Instalación

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r tests/requirements.txt
```

### Configuración

```bash
# Copiar variables de entorno de ejemplo
cp tests/env.test tests/.env.test

# Editar configuración si es necesario
nano tests/env.test
```

## 🧪 Ejecución de Tests

### Ejecutar Todos los Tests

```bash
# Usar el script wrapper (recomendado)
./run-tests.sh

# O ejecutar pytest directamente
pytest tests/
```

### Ejecutar Tests Específicos

```bash
# Tests de un componente específico
pytest tests/test_web.py

# Test específico
pytest tests/test_websocket_url.py::test_public_url_format

# Tests con marcadores específicos
pytest -m "docker"  # Solo tests que requieren Docker
pytest -m "selenium"  # Solo tests de Selenium
pytest -m "not slow"  # Excluir tests lentos
```

### Opciones Avanzadas

```bash
# Con reporte HTML
pytest --html=test-results/report.html

# Con cobertura
pytest --cov=tests

# En paralelo
pytest -n auto

# Con timeout personalizado
pytest --timeout=120

# Solo tests que fallaron anteriormente
pytest --lf
```

## 🔍 Tests Específicos

### Test de URL Malformada WebSocket

**Propósito**: Detecta URLs WebSocket malformadas como `wss://http//localhost:8080` que causan fallos de conexión.

**Errores que detecta**:
- URLs con protocolos duplicados (`wss://http://`)
- URLs con slashes incorrectos (`http//`)
- Configuración incorrecta de `PUBLIC_URL`
- Problemas de construcción de URL en `config.js`

**Ejecución**:
```bash
pytest tests/test_websocket_url.py -v
```

### Test de Error Específico

**Propósito**: Test específico para el error reportado `wss://http//localhost:8080/xmpp-websocket`.

**Características**:
- Detecta el error exacto reportado
- Analiza la causa raíz
- Valida soluciones propuestas
- Simula construcción de URLs

**Ejecución**:
```bash
pytest tests/test_websocket_error_specific.py -v
```

### Test de Selenium

**Propósito**: Test automatizado que usa Selenium para detectar errores directamente en el navegador.

**Características**:
- Detección real de errores en el navegador
- Captura de logs de consola
- Screenshots automáticos
- Reportes JSON estructurados

**Ejecución**:
```bash
# Requiere navegador instalado
pytest tests/test_websocket_selenium.py -v

# O usar el wrapper
./tests/test-websocket-selenium.sh
```

## 📊 Reportes y Resultados

### Tipos de Reportes

- **HTML**: `test-results/report.html` - Reporte visual completo
- **JUnit**: `test-results/junit.xml` - Para integración CI/CD
- **JSON**: `test-results/*.json` - Resultados estructurados
- **Screenshots**: `test-results/screenshots/` - Capturas de errores

### Interpretación de Resultados

- ✅ **PASSED** - Test exitoso
- ❌ **FAILED** - Test falló
- ⚠️ **WARNING** - Advertencias (no críticas)
- ⏭️ **SKIPPED** - Test omitido (dependencias faltantes)

## 🔧 Diagnóstico de Problemas

### Error: "URL malformada detectada"

**Síntomas**:
- WebSocket connection failed en el navegador
- URLs como `wss://http//localhost:8080/xmpp-websocket`

**Diagnóstico**:
```bash
# Verificar variables de entorno
docker compose exec web env | grep -E "(PUBLIC_URL|JITSI_DOMAIN)"

# Verificar configuración del frontend
docker compose exec web cat /usr/share/jitsi-meet/config.js | grep -i websocket
```

**Solución**:
1. Corregir `PUBLIC_URL` en `.env`
2. Reiniciar servicios: `docker compose restart`
3. Verificar que no hay protocolos duplicados

### Error: "Puerto WebSocket no accesible"

**Síntomas**:
- Timeout en conexión WebSocket
- Puerto 5280 no responde

**Diagnóstico**:
```bash
# Verificar que el puerto está mapeado
docker compose ps | grep 5280

# Verificar conectividad
nc -z localhost 5280
```

**Solución**:
1. Verificar mapeo de puertos en `docker-compose.yml`
2. Reiniciar contenedor prosody: `docker compose restart prosody`

## 🛠️ Desarrollo y Mantenimiento

### Agregar Nuevo Test

1. **Crear archivo de test**:
   ```python
   # tests/test_nuevo.py
   import pytest
   
   def test_nueva_funcionalidad():
       """Test de nueva funcionalidad"""
       assert True
   ```

2. **Agregar fixtures si es necesario**:
   ```python
   # En conftest.py
   @pytest.fixture
   def nueva_fixture():
       return "valor"
   ```

3. **Ejecutar test**:
   ```bash
   pytest tests/test_nuevo.py -v
   ```

### Estructura de Test

Cada test debe seguir esta estructura:

```python
import pytest

@pytest.mark.docker  # Si requiere Docker
def test_nombre_descriptivo(fixture_necesaria):
    """Descripción clara del test"""
    # Arrange
    setup_data = fixture_necesaria
    
    # Act
    result = perform_action()
    
    # Assert
    assert result == expected_value
    print("✅ Test completado exitosamente")
```

### Marcadores de Test

- `@pytest.mark.docker` - Tests que requieren Docker
- `@pytest.mark.selenium` - Tests que usan Selenium
- `@pytest.mark.slow` - Tests lentos (>30 segundos)
- `@pytest.mark.integration` - Tests de integración
- `@pytest.mark.unit` - Tests unitarios

## 📚 Variables de Entorno

### Variables de Test

- `JITSI_URL` - URL de Jitsi Meet (default: http://localhost:8080)
- `TEST_ROOM` - Nombre de sala de prueba (default: test-websocket-error)
- `HEADLESS` - Ejecutar Selenium en modo headless (default: true)
- `TEST_TIMEOUT` - Timeout en segundos (default: 30)
- `BROWSER` - Navegador para Selenium (default: chrome)

### Variables de Jitsi

- `PUBLIC_URL` - URL pública de Jitsi Meet
- `JITSI_DOMAIN` - Dominio de Jitsi Meet
- `JICOFO_COMPONENT_SECRET` - Secreto del componente Jicofo
- `JICOFO_AUTH_PASSWORD` - Contraseña de autenticación Jicofo
- `JVB_AUTH_PASSWORD` - Contraseña de autenticación JVB

## 🔄 Integración CI/CD

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
      - name: Run tests
        run: pytest tests/ --html=report.html
```

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY tests/requirements.txt .
RUN pip install -r requirements.txt
COPY tests/ .
CMD ["pytest", "tests/"]
```

## 📝 Logs y Debugging

### Ver Logs de Tests

```bash
# Logs detallados
pytest tests/ -v -s

# Logs de un test específico
pytest tests/test_web.py::test_web_http_accessible -v -s

# Con captura de logs
pytest tests/ --log-cli-level=DEBUG
```

### Debugging

```bash
# Ejecutar con debugger
pytest tests/test_web.py --pdb

# Solo recopilar tests (sin ejecutar)
pytest tests/ --collect-only

# Mostrar fixtures disponibles
pytest --fixtures
```

## 📚 Referencias

- [Documentación oficial de pytest](https://docs.pytest.org/)
- [Documentación oficial de Jitsi Meet](https://jitsi.org/docs/)
- [Selenium WebDriver](https://selenium-python.readthedocs.io/)
- [Docker Python SDK](https://docker-py.readthedocs.io/)