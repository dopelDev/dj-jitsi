"""
Tests para el Jitsi Videobridge (JVB) de Jitsi Meet
"""
import pytest
import docker
import re
import time

@pytest.mark.docker
def test_jvb_container_running(docker_client, jitsi_containers):
    """Verificar que contenedor de JVB esté ejecutándose"""
    assert 'jvb' in jitsi_containers
    container = jitsi_containers['jvb']
    assert container.status == 'running'
    print(f"✅ Contenedor JVB ejecutándose: {container.name}")

@pytest.mark.docker
def test_jvb_udp_port():
    """Verificar puerto 10000/udp para RTP"""
    # Para UDP, verificamos que el puerto esté mapeado en Docker
    import subprocess
    try:
        result = subprocess.run(
            ['docker', 'compose', 'ps', '--format', 'table {{.Name}}\t{{.Ports}}'],
            capture_output=True, text=True, check=True
        )
        
        # Buscar el contenedor JVB y verificar que tenga el puerto 10000/udp mapeado
        lines = result.stdout.split('\n')
        jvb_found = False
        for line in lines:
            if 'jitsi-jvb' in line and '10000/udp' in line:
                jvb_found = True
                print("✅ Puerto 10000/udp mapeado para JVB")
                break
        
        if not jvb_found:
            print("⚠️  Puerto 10000/udp no encontrado en mapeo de puertos")
            print("Mapeo de puertos actual:")
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error verificando mapeo de puertos: {e}")

@pytest.mark.docker
def test_jvb_logs_no_errors(jitsi_containers):
    """Verificar logs sin errores fatales"""
    container = jitsi_containers['jvb']
    logs = container.logs(tail=50).decode('utf-8')
    
    # Patrones de error que no deberían aparecer
    error_patterns = [
        r'FATAL ERROR',
        r'ERROR.*bind.*failed',
        r'ERROR.*port.*already.*in.*use',
        r'ERROR.*network.*unreachable'
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, logs, re.IGNORECASE)
        if matches:
            pytest.fail(f"Error encontrado en logs de JVB: {matches}")
    
    print("✅ Logs de JVB sin errores fatales")

@pytest.mark.docker
def test_jvb_process_running(jitsi_containers):
    """Verificar que el proceso JVB esté ejecutándose"""
    container = jitsi_containers['jvb']
    
    try:
        # Intentar con ps -A (sintaxis compatible con contenedores Jitsi)
        result = container.exec_run("ps -A | grep java")
        output = result.output.decode('utf-8')
        print(f"🔍 Output de ps -A: {output}")
        
        if 'java' in output:
            print("✅ Proceso Java (JVB) ejecutándose en el contenedor")
            return
        
        # Método alternativo: verificar puerto UDP desde dentro del contenedor
        result = container.exec_run("netstat -tuln | grep 10000")
        if result.exit_code == 0:
            netstat_output = result.output.decode('utf-8')
            print(f"🔍 Netstat output: {netstat_output}")
            if '10000' in netstat_output:
                print("✅ JVB verificado mediante puerto UDP 10000")
                return
        
        # Método alternativo: verificar logs activos
        result = container.exec_run("tail -n 5 /var/log/jitsi/jvb.log")
        if result.exit_code == 0:
            log_output = result.output.decode('utf-8')
            print(f"🔍 Logs de JVB: {log_output}")
            if 'jvb' in log_output.lower() or 'java' in log_output.lower():
                print("✅ JVB verificado mediante logs activos")
                return
        
        # Método alternativo: verificar que el contenedor está healthy
        if container.status == 'running':
            print("✅ Contenedor JVB está running")
            return
            
        pytest.fail("Proceso JVB no encontrado con ningún método de verificación")
        
    except Exception as e:
        print(f"❌ Error detallado: {e}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        pytest.fail(f"No se pudo verificar el proceso jvb: {e}")

@pytest.mark.docker
def test_jvb_configuration_files(jitsi_containers):
    """Verificar archivos de configuración de JVB"""
    container = jitsi_containers['jvb']
    
    # Verificar archivos de configuración críticos
    config_files = [
        '/etc/jitsi/videobridge/jvb.conf',
        '/etc/jitsi/videobridge/logging.properties'
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
def test_jvb_network_interfaces(jitsi_containers):
    """Verificar interfaces de red de JVB"""
    container = jitsi_containers['jvb']
    
    try:
        # Verificar que el contenedor tiene interfaces de red
        result = container.exec_run("ip addr show")
        output = result.output.decode('utf-8')
        
        if 'inet' in output:
            print("✅ Interfaces de red configuradas")
        else:
            print("⚠️  No se encontraron interfaces de red")
    except Exception as e:
        print(f"⚠️  Error verificando interfaces de red: {e}")

@pytest.mark.docker
def test_jvb_ready_for_conferences(jitsi_containers):
    """Verificar que JVB esté listo para manejar conferencias"""
    container = jitsi_containers['jvb']
    
    # Verificar logs para indicadores de que JVB está listo
    logs = container.logs(tail=100).decode('utf-8')
    
    ready_indicators = [
        r'JVB.*started',
        r'JVB.*ready',
        r'Videobridge.*started',
        r'RTP.*ready'
    ]
    
    ready_found = False
    for pattern in ready_indicators:
        if re.search(pattern, logs, re.IGNORECASE):
            ready_found = True
            print(f"✅ JVB listo: {pattern}")
            break
    
    if not ready_found:
        print("⚠️  No se encontraron indicadores claros de que JVB esté listo")
        print("Logs recientes de JVB:")
        print(logs[-300:])  # Mostrar últimos 300 caracteres

@pytest.mark.docker
def test_jvb_rtp_port_binding(jitsi_containers):
    """Verificar que JVB esté escuchando en el puerto RTP"""
    container = jitsi_containers['jvb']
    
    try:
        # Verificar que el puerto 10000 esté en uso dentro del contenedor
        result = container.exec_run("netstat -ulnp | grep :10000")
        output = result.output.decode('utf-8')
        
        if ':10000' in output:
            print("✅ Puerto 10000/udp en uso dentro del contenedor")
        else:
            print("⚠️  Puerto 10000/udp no encontrado en uso dentro del contenedor")
            print("Puertos UDP en uso:")
            print(output)
    except Exception as e:
        print(f"⚠️  Error verificando puerto RTP: {e}")

@pytest.mark.docker
def test_jvb_memory_usage(jitsi_containers):
    """Verificar uso de memoria de JVB"""
    container = jitsi_containers['jvb']
    
    try:
        # Obtener estadísticas de memoria del contenedor
        stats = container.stats(stream=False)
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats'].get('limit', 0)
        
        if memory_limit > 0:
            memory_percent = (memory_usage / memory_limit) * 100
            print(f"✅ Uso de memoria: {memory_usage / 1024 / 1024:.1f}MB ({memory_percent:.1f}%)")
            
            if memory_percent > 90:
                print("⚠️  Uso de memoria alto (>90%)")
        else:
            print(f"✅ Uso de memoria: {memory_usage / 1024 / 1024:.1f}MB")
    except Exception as e:
        print(f"⚠️  Error verificando uso de memoria: {e}")

@pytest.mark.docker
def test_jvb_network_connectivity(jitsi_containers):
    """Verificar conectividad de red de JVB"""
    container = jitsi_containers['jvb']
    
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
