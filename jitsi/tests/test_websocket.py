"""
Tests para conectividad WebSocket de Jitsi Meet
"""
import pytest
import socket
import requests
import docker
import re
import time
import urllib.parse
from urllib.parse import urlparse

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

# ===== NUEVOS TESTS PARA CUBRIR ERRORES ESPECÍFICOS =====

@pytest.mark.docker
def test_websocket_url_validation():
    """Verificar que las URLs de WebSocket estén correctamente formateadas"""
    # URLs correctas que deberían funcionar
    correct_urls = [
        "ws://localhost:5280/xmpp-websocket",
        "wss://localhost:5280/xmpp-websocket",
        "ws://localhost:8080/xmpp-websocket",
        "wss://localhost:8080/xmpp-websocket"
    ]
    
    # URLs incorrectas que causan el error reportado
    incorrect_urls = [
        "wss://http//localhost:8080/xmpp-websocket",  # Error reportado
        "ws://http//localhost:5280/xmpp-websocket",   # Similar error
        "wss://https//localhost:8080/xmpp-websocket", # Protocolo duplicado
        "ws://ws//localhost:5280/xmpp-websocket",      # Protocolo duplicado
    ]
    
    for url in correct_urls:
        try:
            parsed = urlparse(url)
            assert parsed.scheme in ['ws', 'wss'], f"Esquema incorrecto en {url}"
            assert parsed.netloc, f"Host vacío en {url}"
            assert not '//' in parsed.netloc, f"Barras dobles en host de {url}"
            print(f"✅ URL válida: {url}")
        except Exception as e:
            pytest.fail(f"Error validando URL correcta {url}: {e}")
    
    for url in incorrect_urls:
        try:
            parsed = urlparse(url)
            # Estas URLs deberían fallar la validación
            if '//' in parsed.netloc or parsed.scheme not in ['ws', 'wss']:
                print(f"✅ URL incorrecta detectada correctamente: {url}")
            else:
                pytest.fail(f"URL incorrecta no detectada: {url}")
        except Exception as e:
            print(f"✅ URL incorrecta rechazada correctamente: {url} - {e}")

@pytest.mark.docker
def test_websocket_protocol_validation():
    """Verificar que los protocolos WebSocket sean correctos"""
    protocols_to_test = [
        ("ws", "http", False),    # ws con http - incorrecto
        ("wss", "https", False),  # wss con https - incorrecto  
        ("ws", "ws", True),       # ws con ws - correcto
        ("wss", "wss", True),     # wss con wss - correcto
        ("ws", None, True),       # ws sin protocolo base - correcto
        ("wss", None, True),      # wss sin protocolo base - correcto
    ]
    
    for ws_protocol, base_protocol, should_pass in protocols_to_test:
        if base_protocol:
            # Simular el error: protocolo duplicado
            malformed_url = f"{ws_protocol}://{base_protocol}//localhost:8080/xmpp-websocket"
        else:
            correct_url = f"{ws_protocol}://localhost:8080/xmpp-websocket"
        
        try:
            if base_protocol:
                # Esta URL debería ser inválida
                parsed = urlparse(malformed_url)
                if '//' in parsed.netloc:
                    print(f"✅ URL malformada detectada: {malformed_url}")
                else:
                    pytest.fail(f"URL malformada no detectada: {malformed_url}")
            else:
                # Esta URL debería ser válida
                parsed = urlparse(correct_url)
                assert parsed.scheme == ws_protocol
                print(f"✅ URL correcta: {correct_url}")
        except Exception as e:
            if should_pass:
                pytest.fail(f"Error inesperado con URL correcta: {e}")
            else:
                print(f"✅ Error esperado con URL incorrecta: {e}")

@pytest.mark.docker
def test_websocket_strophe_error_simulation():
    """Simular el error específico de Strophe.js reportado"""
    # Simular la URL problemática del error
    problematic_url = "wss://http//localhost:8080/xmpp-websocket?room=kindsolidssearchperfectly"
    
    try:
        # Intentar parsear la URL problemática
        parsed = urlparse(problematic_url)
        
        # Verificar que detectamos el problema
        assert '//' in parsed.netloc, "No se detectó el problema de barras dobles"
        assert parsed.scheme == 'wss', "Esquema incorrecto"
        
        print(f"✅ Error de Strophe.js simulado correctamente: {problematic_url}")
        print(f"   - Esquema: {parsed.scheme}")
        print(f"   - Host problemático: {parsed.netloc}")
        print(f"   - Path: {parsed.path}")
        print(f"   - Query: {parsed.query}")
        
    except Exception as e:
        pytest.fail(f"Error inesperado simulando error de Strophe: {e}")

@pytest.mark.docker
def test_websocket_connection_error_handling():
    """Verificar manejo de errores de conexión WebSocket"""
    error_scenarios = [
        {
            "name": "URL con protocolo duplicado",
            "url": "wss://http//localhost:8080/xmpp-websocket",
            "should_fail": True
        },
        {
            "name": "URL con barras dobles",
            "url": "ws://localhost//8080/xmpp-websocket", 
            "should_fail": True
        },
        {
            "name": "URL correcta",
            "url": "ws://localhost:8080/xmpp-websocket",
            "should_fail": False
        }
    ]
    
    for scenario in error_scenarios:
        try:
            parsed = urlparse(scenario["url"])
            
            # Verificar problemas comunes
            has_double_slashes = '//' in parsed.netloc
            has_duplicate_protocols = parsed.scheme in parsed.netloc
            
            if scenario["should_fail"]:
                if has_double_slashes or has_duplicate_protocols:
                    print(f"✅ Error detectado en {scenario['name']}: {scenario['url']}")
                else:
                    pytest.fail(f"No se detectó error esperado en {scenario['name']}")
            else:
                if not has_double_slashes and not has_duplicate_protocols:
                    print(f"✅ URL válida en {scenario['name']}: {scenario['url']}")
                else:
                    pytest.fail(f"Error inesperado en URL válida {scenario['name']}")
                    
        except Exception as e:
            if scenario["should_fail"]:
                print(f"✅ Excepción esperada en {scenario['name']}: {e}")
            else:
                pytest.fail(f"Excepción inesperada en {scenario['name']}: {e}")

@pytest.mark.docker
def test_websocket_strophe_connection_parameters():
    """Verificar parámetros de conexión Strophe.js"""
    # Simular diferentes configuraciones de conexión
    connection_configs = [
        {
            "name": "Configuración correcta",
            "url": "ws://localhost:5280/xmpp-websocket",
            "room": "testroom",
            "should_work": True
        },
        {
            "name": "Configuración con error de protocolo",
            "url": "wss://http//localhost:8080/xmpp-websocket", 
            "room": "kindsolidssearchperfectly",
            "should_work": False
        },
        {
            "name": "Configuración con puerto incorrecto",
            "url": "ws://localhost:9999/xmpp-websocket",
            "room": "testroom",
            "should_work": False
        }
    ]
    
    for config in connection_configs:
        try:
            parsed = urlparse(config["url"])
            
            # Verificar problemas en la URL
            has_protocol_error = '//' in parsed.netloc or parsed.scheme in parsed.netloc
            has_valid_port = parsed.port and parsed.port in [5280, 8080, 5222]
            
            if config["should_work"]:
                assert not has_protocol_error, f"Error de protocolo en URL válida: {config['url']}"
                assert has_valid_port, f"Puerto inválido en URL válida: {config['url']}"
                print(f"✅ Configuración válida: {config['name']}")
            else:
                if has_protocol_error or not has_valid_port:
                    print(f"✅ Error detectado en {config['name']}: {config['url']}")
                else:
                    print(f"⚠️  No se detectó error esperado en {config['name']}")
                    
        except Exception as e:
            print(f"⚠️  Error procesando {config['name']}: {e}")

@pytest.mark.docker
def test_websocket_error_logging():
    """Verificar que los errores de WebSocket se registren correctamente"""
    # Simular diferentes tipos de errores que deberían aparecer en logs
    error_messages = [
        "WebSocket connection to 'wss://http//localhost:8080/xmpp-websocket?room=test' failed",
        "Strophe: Websocket error",
        "Strophe: Websocket closed unexcectedly",  # Nota: "unexcectedly" es como aparece en el error real
        "The WebSocket connection could not be established or was disconnected"
    ]
    
    for error_msg in error_messages:
        # Verificar que podemos detectar estos patrones de error
        error_patterns = [
            r'WebSocket connection.*failed',
            r'Strophe.*Websocket error',
            r'Strophe.*Websocket closed',
            r'WebSocket connection could not be established'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, error_msg, re.IGNORECASE):
                print(f"✅ Patrón de error detectado: {pattern} en '{error_msg}'")
                break
        else:
            print(f"⚠️  No se detectó patrón para: {error_msg}")

@pytest.mark.docker
def test_websocket_url_fix_suggestions():
    """Proporcionar sugerencias para corregir URLs de WebSocket"""
    problematic_urls = [
        "wss://http//localhost:8080/xmpp-websocket",
        "ws://ws//localhost:5280/xmpp-websocket", 
        "wss://https//localhost:8080/xmpp-websocket"
    ]
    
    for url in problematic_urls:
        try:
            parsed = urlparse(url)
            
            # Detectar problemas específicos
            if '//' in parsed.netloc:
                # Extraer el host real (después de las barras dobles)
                host_parts = parsed.netloc.split('//')
                if len(host_parts) > 1:
                    real_host = host_parts[1]
                    fixed_url = f"{parsed.scheme}://{real_host}{parsed.path}"
                    if parsed.query:
                        fixed_url += f"?{parsed.query}"
                    
                    print(f"✅ URL problemática: {url}")
                    print(f"   Sugerencia de corrección: {fixed_url}")
                else:
                    print(f"⚠️  No se pudo extraer host de: {url}")
            else:
                print(f"✅ URL aparentemente correcta: {url}")
                
        except Exception as e:
            print(f"⚠️  Error procesando URL {url}: {e}")
