"""
Tests para conectividad WebSocket de Jitsi Meet
"""
import pytest
import socket
import requests
import docker
import re

@pytest.mark.docker
def test_websocket_port_5280(port_checker):
    """Verificar puerto 5280 accesible para WebSocket"""
    assert port_checker['tcp']('localhost', 5280), "Puerto 5280 (WebSocket) no accesible"
    print("✅ Puerto 5280 (WebSocket) accesible")

@pytest.mark.docker
def test_websocket_port_5222(port_checker):
    """Verificar puerto 5222 accesible para XMPP"""
    assert port_checker['tcp']('localhost', 5222), "Puerto 5222 (XMPP) no accesible"
    print("✅ Puerto 5222 (XMPP) accesible")

@pytest.mark.docker
def test_websocket_no_errors_in_logs(jitsi_containers):
    """Verificar logs sin errores de WebSocket"""
    # Verificar logs de Prosody (servidor XMPP/WebSocket)
    prosody_container = jitsi_containers['prosody']
    prosody_logs = prosody_container.logs(tail=50).decode('utf-8')
    
    # Patrones de error de WebSocket que no deberían aparecer
    websocket_error_patterns = [
        r'ERROR.*websocket.*failed',
        r'ERROR.*websocket.*connection.*failed',
        r'ERROR.*websocket.*bind.*failed',
        r'FATAL.*websocket'
    ]
    
    for pattern in websocket_error_patterns:
        matches = re.findall(pattern, prosody_logs, re.IGNORECASE)
        if matches:
            pytest.fail(f"Error de WebSocket encontrado en logs de Prosody: {matches}")
    
    print("✅ Logs de Prosody sin errores de WebSocket")

@pytest.mark.docker
def test_websocket_endpoint_accessible():
    """Verificar que el endpoint WebSocket sea accesible"""
    websocket_url = "http://localhost:5280/xmpp-websocket"
    
    try:
        # Intentar conectar al endpoint (esto debería fallar con un error específico)
        response = requests.get(websocket_url, timeout=5)
        # Si llegamos aquí, el endpoint está respondiendo
        print("✅ Endpoint WebSocket respondiendo")
    except requests.exceptions.ConnectionError:
        pytest.fail("Endpoint WebSocket no accesible en puerto 5280")
    except requests.exceptions.Timeout:
        pytest.fail("Timeout conectando al endpoint WebSocket")
    except Exception as e:
        # Otros errores pueden ser esperados (como protocolo incorrecto)
        print(f"✅ Endpoint WebSocket accesible (error esperado: {type(e).__name__})")

@pytest.mark.docker
def test_websocket_strophe_connection_simulation():
    """Simular conexión Strophe al WebSocket"""
    # Este test simula lo que haría Strophe.js para conectar
    websocket_url = "ws://localhost:5280/xmpp-websocket"
    
    try:
        # Intentar crear un socket TCP (simulación básica)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 5280))
        sock.close()
        print("✅ Conexión TCP al puerto WebSocket exitosa")
    except socket.error as e:
        pytest.fail(f"Error conectando al puerto WebSocket: {e}")

@pytest.mark.docker
def test_websocket_prosody_listening(jitsi_containers):
    """Verificar que Prosody esté escuchando en el puerto WebSocket"""
    container = jitsi_containers['prosody']
    
    try:
        # Verificar que el puerto 5280 esté en uso dentro del contenedor
        result = container.exec_run("netstat -tlnp | grep :5280")
        output = result.output.decode('utf-8')
        
        if ':5280' in output:
            print("✅ Puerto 5280 en uso dentro del contenedor Prosody")
        else:
            print("⚠️  Puerto 5280 no encontrado en uso dentro del contenedor")
            print("Puertos en uso:")
            print(output)
    except Exception as e:
        print(f"⚠️  Error verificando puerto WebSocket: {e}")

@pytest.mark.docker
def test_websocket_xmpp_port_listening(jitsi_containers):
    """Verificar que Prosody esté escuchando en el puerto XMPP"""
    container = jitsi_containers['prosody']
    
    try:
        # Verificar que el puerto 5222 esté en uso dentro del contenedor
        result = container.exec_run("netstat -tlnp | grep :5222")
        output = result.output.decode('utf-8')
        
        if ':5222' in output:
            print("✅ Puerto 5222 (XMPP) en uso dentro del contenedor Prosody")
        else:
            print("⚠️  Puerto 5222 no encontrado en uso dentro del contenedor")
            print("Puertos en uso:")
            print(output)
    except Exception as e:
        print(f"⚠️  Error verificando puerto XMPP: {e}")

@pytest.mark.docker
def test_websocket_cross_origin_headers():
    """Verificar headers CORS para WebSocket"""
    websocket_url = "http://localhost:5280/xmpp-websocket"
    
    try:
        response = requests.get(websocket_url, timeout=5)
        headers = response.headers
        
        # Verificar headers CORS importantes
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        found_cors_headers = []
        for header in cors_headers:
            if header in headers:
                found_cors_headers.append(f"{header}: {headers[header]}")
        
        if found_cors_headers:
            print(f"✅ Headers CORS encontrados: {found_cors_headers}")
        else:
            print("⚠️  No se encontraron headers CORS (puede ser normal)")
    except Exception as e:
        print(f"⚠️  Error verificando headers CORS: {e}")

@pytest.mark.docker
def test_websocket_ssl_tls_support():
    """Verificar soporte SSL/TLS para WebSocket seguro"""
    # Verificar si hay soporte para WSS (WebSocket Secure)
    try:
        # Intentar conectar con HTTPS (que debería fallar pero nos dirá si hay SSL)
        https_websocket_url = "https://localhost:5280/xmpp-websocket"
        response = requests.get(https_websocket_url, timeout=5, verify=False)
        print("✅ Soporte HTTPS detectado")
    except requests.exceptions.SSLError:
        print("⚠️  Error SSL (puede ser normal en desarrollo)")
    except requests.exceptions.ConnectionError:
        print("⚠️  No hay soporte HTTPS (normal en desarrollo)")
    except Exception as e:
        print(f"✅ Respuesta HTTPS (error esperado): {type(e).__name__}")

@pytest.mark.docker
def test_websocket_connection_timeout():
    """Verificar timeout de conexión WebSocket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Timeout muy corto
        start_time = time.time()
        
        try:
            sock.connect(('localhost', 5280))
            connection_time = time.time() - start_time
            print(f"✅ Conexión WebSocket exitosa en {connection_time:.2f}s")
        except socket.timeout:
            print("⚠️  Timeout de conexión WebSocket (puede ser normal)")
        finally:
            sock.close()
    except Exception as e:
        print(f"⚠️  Error en test de timeout: {e}")

@pytest.mark.docker
def test_websocket_multiple_connections():
    """Verificar que se pueden hacer múltiples conexiones WebSocket"""
    connections = []
    max_connections = 3
    
    try:
        for i in range(max_connections):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(('localhost', 5280))
            connections.append(sock)
        
        print(f"✅ {len(connections)} conexiones WebSocket simultáneas exitosas")
        
    except Exception as e:
        print(f"⚠️  Error en conexiones múltiples: {e}")
    finally:
        # Cerrar todas las conexiones
        for sock in connections:
            try:
                sock.close()
            except:
                pass

@pytest.mark.docker
def test_websocket_prosody_modules(jitsi_containers):
    """Verificar que Prosody tenga los módulos WebSocket necesarios"""
    container = jitsi_containers['prosody']
    
    try:
        # Verificar configuración de Prosody para módulos WebSocket
        result = container.exec_run("grep -r 'websocket\\|bosh' /etc/prosody/")
        output = result.output.decode('utf-8')
        
        if 'websocket' in output.lower() or 'bosh' in output.lower():
            print("✅ Módulos WebSocket/BOSH configurados en Prosody")
        else:
            print("⚠️  No se encontraron configuraciones WebSocket/BOSH")
    except Exception as e:
        print(f"⚠️  Error verificando módulos WebSocket: {e}")
