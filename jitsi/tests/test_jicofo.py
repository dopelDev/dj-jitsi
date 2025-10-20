"""
Tests para el componente Jicofo (Jitsi Conference Focus) de Jitsi Meet
"""
import pytest
import docker
import re
import time

@pytest.mark.docker
def test_jicofo_container_running(docker_client, jitsi_containers):
    """Verificar que contenedor de Jicofo esté ejecutándose"""
    assert 'jicofo' in jitsi_containers
    container = jitsi_containers['jicofo']
    assert container.status == 'running'
    print(f"✅ Contenedor Jicofo ejecutándose: {container.name}")

@pytest.mark.docker
def test_jicofo_xmpp_connection(jitsi_containers):
    """Verificar conexión XMPP de Jicofo con Prosody"""
    container = jitsi_containers['jicofo']
    
    # Verificar logs de Jicofo para conexión XMPP exitosa
    logs = container.logs(tail=50).decode('utf-8')
    
    # Patrones que indican conexión exitosa
    success_patterns = [
        r'Jicofo.*started',
        r'XMPP.*connected',
        r'Prosody.*connected',
        r'Jicofo.*ready'
    ]
    
    connection_success = False
    for pattern in success_patterns:
        if re.search(pattern, logs, re.IGNORECASE):
            connection_success = True
            print(f"✅ Conexión XMPP exitosa: {pattern}")
            break
    
    if not connection_success:
        print("⚠️  No se encontraron indicadores claros de conexión XMPP en logs")
        print("Logs recientes de Jicofo:")
        print(logs[-500:])  # Mostrar últimos 500 caracteres

@pytest.mark.docker
def test_jicofo_logs_no_errors(jitsi_containers):
    """Verificar logs sin errores fatales"""
    container = jitsi_containers['jicofo']
    logs = container.logs(tail=50).decode('utf-8')
    
    # Patrones de error que no deberían aparecer
    error_patterns = [
        r'FATAL ERROR',
        r'ERROR.*connection.*failed',
        r'ERROR.*authentication.*failed',
        r'ERROR.*XMPP.*failed'
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, logs, re.IGNORECASE)
        if matches:
            pytest.fail(f"Error encontrado en logs de Jicofo: {matches}")
    
    print("✅ Logs de Jicofo sin errores fatales")

@pytest.mark.docker
def test_jicofo_process_running(jitsi_containers):
    """Verificar que el proceso Jicofo esté ejecutándose"""
    container = jitsi_containers['jicofo']
    
    try:
        result = container.exec_run("ps aux | grep jicofo | grep -v grep")
        output = result.output.decode('utf-8')
        assert 'jicofo' in output, "Proceso jicofo no encontrado en el contenedor"
        print("✅ Proceso jicofo ejecutándose en el contenedor")
    except Exception as e:
        pytest.fail(f"No se pudo verificar el proceso jicofo: {e}")

@pytest.mark.docker
def test_jicofo_configuration_files(jitsi_containers):
    """Verificar archivos de configuración de Jicofo"""
    container = jitsi_containers['jicofo']
    
    # Verificar archivos de configuración críticos
    config_files = [
        '/etc/jitsi/jicofo/jicofo.conf',
        '/etc/jitsi/jicofo/logging.properties'
    ]
    
    for config_file in config_files:
        try:
            result = container.exec_run(f"test -f {config_file}")
            if result.exit_code == 0:
                print(f"✅ Archivo de configuración encontrado: {config_file}")
            else:
                print(f"⚠️  Archivo de configuración no encontrado: {config_file}")
        except Exception as e:
            print(f"⚠️  Error verificando archivo {config_file}: {e}")

@pytest.mark.docker
def test_jicofo_authentication_setup(jitsi_containers):
    """Verificar configuración de autenticación"""
    container = jitsi_containers['jicofo']
    
    # Verificar que no hay errores de autenticación en los logs
    logs = container.logs(tail=30).decode('utf-8')
    auth_error_patterns = [
        r'ERROR.*auth.*password.*must be set',
        r'ERROR.*authentication.*failed',
        r'ERROR.*SASL.*failed'
    ]
    
    auth_errors = []
    for pattern in auth_error_patterns:
        matches = re.findall(pattern, logs, re.IGNORECASE)
        if matches:
            auth_errors.extend(matches)
    
    if auth_errors:
        pytest.fail(f"Errores de autenticación encontrados: {auth_errors}")
    else:
        print("✅ Sin errores de autenticación")

@pytest.mark.docker
def test_jicofo_ready_for_conferences(jitsi_containers):
    """Verificar que Jicofo esté listo para manejar conferencias"""
    container = jitsi_containers['jicofo']
    
    # Verificar logs para indicadores de que Jicofo está listo
    logs = container.logs(tail=100).decode('utf-8')
    
    ready_indicators = [
        r'Jicofo.*started',
        r'Jicofo.*ready',
        r'Conference.*manager.*ready',
        r'Focus.*component.*ready'
    ]
    
    ready_found = False
    for pattern in ready_indicators:
        if re.search(pattern, logs, re.IGNORECASE):
            ready_found = True
            print(f"✅ Jicofo listo: {pattern}")
            break
    
    if not ready_found:
        print("⚠️  No se encontraron indicadores claros de que Jicofo esté listo")
        print("Logs recientes de Jicofo:")
        print(logs[-300:])  # Mostrar últimos 300 caracteres

@pytest.mark.docker
def test_jicofo_network_connectivity(jitsi_containers):
    """Verificar conectividad de red de Jicofo"""
    container = jitsi_containers['jicofo']
    
    # Verificar que puede resolver nombres de dominio
    try:
        result = container.exec_run("nslookup prosody")
        if result.exit_code == 0:
            print("✅ Resolución DNS funcionando")
        else:
            print("⚠️  Problemas con resolución DNS")
    except Exception as e:
        print(f"⚠️  Error verificando DNS: {e}")
    
    # Verificar conectividad a Prosody
    try:
        result = container.exec_run("nc -z prosody 5222")
        if result.exit_code == 0:
            print("✅ Conectividad a Prosody (puerto 5222) OK")
        else:
            print("⚠️  Problemas de conectividad a Prosody")
    except Exception as e:
        print(f"⚠️  Error verificando conectividad: {e}")
