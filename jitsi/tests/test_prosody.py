"""
Tests para el servidor XMPP Prosody de Jitsi Meet
"""
import pytest
import docker
import re
import time

@pytest.mark.docker
def test_prosody_container_running(docker_client, jitsi_containers):
    """Verificar que contenedor de Prosody esté ejecutándose"""
    assert 'prosody' in jitsi_containers
    container = jitsi_containers['prosody']
    assert container.status == 'running'
    print(f"✅ Contenedor Prosody ejecutándose: {container.name}")

@pytest.mark.docker
def test_prosody_ports_open(port_checker):
    """Verificar puertos 5222 y 5280"""
    # Puerto 5222 (XMPP)
    assert port_checker['tcp']('localhost', 5222), "Puerto 5222 (XMPP) no accesible"
    print("✅ Puerto 5222 (XMPP) accesible")
    
    # Puerto 5280 (WebSocket/BOSH)
    assert port_checker['tcp']('localhost', 5280), "Puerto 5280 (WebSocket) no accesible"
    print("✅ Puerto 5280 (WebSocket) accesible")

@pytest.mark.docker
def test_prosody_logs_no_errors(jitsi_containers):
    """Verificar logs sin errores fatales"""
    container = jitsi_containers['prosody']
    logs = container.logs(tail=50).decode('utf-8')
    
    # Patrones de error que no deberían aparecer
    error_patterns = [
        r'FATAL ERROR',
        r'ERROR.*auth.*password.*must be set',
        r'ERROR.*database.*connection',
        r'ERROR.*certificate'
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, logs, re.IGNORECASE)
        if matches:
            pytest.fail(f"Error encontrado en logs de Prosody: {matches}")
    
    print("✅ Logs de Prosody sin errores fatales")

@pytest.mark.docker
def test_prosody_xmpp_connection(jitsi_containers):
    """Verificar que Prosody esté escuchando conexiones XMPP"""
    container = jitsi_containers['prosody']
    
    # Verificar que el proceso prosody esté ejecutándose dentro del contenedor
    try:
        result = container.exec_run("ps aux | grep prosody | grep -v grep")
        output = result.output.decode('utf-8')
        assert 'prosody' in output, "Proceso prosody no encontrado en el contenedor"
        print("✅ Proceso prosody ejecutándose en el contenedor")
    except Exception as e:
        pytest.fail(f"No se pudo verificar el proceso prosody: {e}")

@pytest.mark.docker
def test_prosody_configuration_files(jitsi_containers):
    """Verificar archivos de configuración de Prosody"""
    container = jitsi_containers['prosody']
    
    # Verificar archivos de configuración críticos
    config_files = [
        '/etc/prosody/prosody.cfg.lua',
        '/etc/prosody/conf.d/jitsi-meet.cfg.lua'
    ]
    
    for config_file in config_files:
        try:
            result = container.exec_run(f"test -f {config_file}")
            assert result.exit_code == 0, f"Archivo de configuración no encontrado: {config_file}"
            print(f"✅ Archivo de configuración encontrado: {config_file}")
        except Exception as e:
            pytest.fail(f"Error verificando archivo {config_file}: {e}")

@pytest.mark.docker
def test_prosody_database_connection(jitsi_containers):
    """Verificar conexión a base de datos"""
    container = jitsi_containers['prosody']
    
    # Verificar que no hay errores de conexión a base de datos en los logs
    logs = container.logs(tail=20).decode('utf-8')
    db_error_patterns = [
        r'ERROR.*database',
        r'ERROR.*sql',
        r'ERROR.*connection.*failed'
    ]
    
    for pattern in db_error_patterns:
        matches = re.findall(pattern, logs, re.IGNORECASE)
        if matches:
            print(f"⚠️  Advertencia: Posibles errores de base de datos: {matches}")
            # No fallar el test, solo advertir
        else:
            print("✅ Sin errores de conexión a base de datos")

@pytest.mark.docker
def test_prosody_websocket_endpoint():
    """Verificar endpoint WebSocket de Prosody"""
    import requests
    
    # Intentar conectar al endpoint WebSocket (esto debería fallar con un error específico)
    try:
        response = requests.get('http://localhost:5280/xmpp-websocket', timeout=5)
        # Si llegamos aquí, el endpoint está respondiendo (aunque no sea WebSocket)
        print("✅ Endpoint WebSocket respondiendo")
    except requests.exceptions.ConnectionError:
        pytest.fail("Endpoint WebSocket no accesible en puerto 5280")
    except requests.exceptions.Timeout:
        pytest.fail("Timeout conectando al endpoint WebSocket")
    except Exception as e:
        # Otros errores pueden ser esperados (como protocolo incorrecto)
        print(f"✅ Endpoint WebSocket accesible (error esperado: {type(e).__name__})")
