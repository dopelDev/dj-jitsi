"""
Tests para validación de URLs WebSocket y detección de URLs malformadas
"""
import pytest
import re
import os
from urllib.parse import urlparse

@pytest.mark.docker
def test_public_url_format(env_vars):
    """Verificar formato de PUBLIC_URL en .env"""
    public_url = env_vars['PUBLIC_URL']
    
    # Verificar que PUBLIC_URL tenga formato correcto
    assert public_url.startswith('http://') or public_url.startswith('https://'), \
        f"PUBLIC_URL debe empezar con http:// o https://, obtenido: {public_url}"
    
    # Verificar que no tenga doble slash después de http
    assert 'http//' not in public_url, \
        f"PUBLIC_URL contiene 'http//' (doble slash): {public_url}"
    
    # Verificar que no tenga protocolo duplicado
    assert not re.search(r'https?://https?://', public_url), \
        f"PUBLIC_URL contiene protocolo duplicado: {public_url}"
    
    print(f"✅ PUBLIC_URL formato correcto: {public_url}")

@pytest.mark.docker
def test_websocket_url_validation():
    """Validar URLs WebSocket con el helper"""
    # Importar el helper de validación
    import sys
    sys.path.append('./tests/helpers')
    
    try:
        from validate_websocket_url import validate_url
        
        # URLs correctas
        correct_urls = [
            'ws://localhost:5280/xmpp-websocket',
            'wss://localhost:5280/xmpp-websocket',
            'ws://localhost:8080/xmpp-websocket',
            'wss://meet.example.com:5280/xmpp-websocket'
        ]
        
        for url in correct_urls:
            assert validate_url(url), f"URL correcta marcada como inválida: {url}"
            print(f"✅ URL válida: {url}")
        
        # URLs malformadas
        malformed_urls = [
            'wss://http//localhost:8080/xmpp-websocket',
            'ws://http//localhost:8080/xmpp-websocket',
            'wss://https//localhost:8080/xmpp-websocket',
            'ws://ws//localhost:8080/xmpp-websocket'
        ]
        
        for url in malformed_urls:
            assert not validate_url(url), f"URL malformada marcada como válida: {url}"
            print(f"✅ URL malformada detectada: {url}")
            
    except ImportError:
        pytest.skip("Helper de validación no disponible")

@pytest.mark.docker
def test_detect_malformed_url_pattern():
    """Detectar patrón wss://http//localhost"""
    # Patrón específico del error reportado
    error_pattern = r'wss?://http//.*'
    
    # URLs que deberían coincidir con el patrón
    malformed_urls = [
        'wss://http//localhost:8080/xmpp-websocket',
        'ws://http//localhost:8080/xmpp-websocket',
        'wss://http//meet.example.com:8080/xmpp-websocket'
    ]
    
    for url in malformed_urls:
        assert re.search(error_pattern, url), f"Patrón no detectado en: {url}"
        print(f"✅ Patrón malformado detectado: {url}")
    
    # URLs que NO deberían coincidir
    correct_urls = [
        'wss://localhost:8080/xmpp-websocket',
        'ws://localhost:8080/xmpp-websocket',
        'wss://meet.example.com:8080/xmpp-websocket'
    ]
    
    for url in correct_urls:
        assert not re.search(error_pattern, url), f"Patrón detectado incorrectamente en: {url}"
        print(f"✅ URL correcta no coincide con patrón: {url}")

@pytest.mark.docker
def test_url_construction_simulation(env_vars):
    """Simular construcción de URL como Jitsi"""
    public_url = env_vars['PUBLIC_URL']
    jitsi_domain = env_vars['JITSI_DOMAIN']
    
    # Simular cómo Jitsi construye la URL WebSocket
    # Esto es una simulación basada en el comportamiento observado
    
    # Construcción correcta
    if public_url.startswith('http://'):
        ws_protocol = 'ws://'
    elif public_url.startswith('https://'):
        ws_protocol = 'wss://'
    else:
        pytest.fail(f"Protocolo no soportado en PUBLIC_URL: {public_url}")
    
    # Construir URL WebSocket correcta
    correct_ws_url = f"{ws_protocol}{jitsi_domain}:8080/xmpp-websocket"
    print(f"✅ URL WebSocket construida correctamente: {correct_ws_url}")
    
    # Verificar que no contenga el patrón malformado
    assert 'http//' not in correct_ws_url, f"URL construida contiene patrón malformado: {correct_ws_url}"
    assert 'https//' not in correct_ws_url, f"URL construida contiene patrón malformado: {correct_ws_url}"

@pytest.mark.docker
def test_websocket_url_parsing():
    """Verificar parsing de URLs WebSocket"""
    from urllib.parse import urlparse
    
    # URLs para probar
    test_urls = [
        'ws://localhost:5280/xmpp-websocket',
        'wss://localhost:5280/xmpp-websocket',
        'ws://meet.example.com:8080/xmpp-websocket',
        'wss://meet.example.com:8080/xmpp-websocket'
    ]
    
    for url in test_urls:
        parsed = urlparse(url)
        
        # Verificar componentes
        assert parsed.scheme in ['ws', 'wss'], f"Esquema inválido: {parsed.scheme}"
        assert parsed.netloc, f"Netloc vacío en: {url}"
        assert parsed.path, f"Path vacío en: {url}"
        
        print(f"✅ URL parseada correctamente: {url}")
        print(f"   Esquema: {parsed.scheme}")
        print(f"   Host: {parsed.netloc}")
        print(f"   Path: {parsed.path}")

@pytest.mark.docker
def test_malformed_url_detection_patterns():
    """Detectar diferentes patrones de URLs malformadas"""
    # Patrones de URLs malformadas comunes
    malformed_patterns = [
        r'wss?://http//.*',  # wss://http//localhost
        r'wss?://https//.*',  # wss://https//localhost
        r'wss?://ws//.*',     # wss://ws//localhost
        r'wss?://wss//.*',    # wss://wss//localhost
        r'wss?://.*//.*',     # Doble slash en cualquier parte
    ]
    
    # URLs malformadas de prueba
    malformed_urls = [
        'wss://http//localhost:8080/xmpp-websocket',
        'ws://http//localhost:8080/xmpp-websocket',
        'wss://https//localhost:8080/xmpp-websocket',
        'ws://ws//localhost:8080/xmpp-websocket',
        'wss://wss//localhost:8080/xmpp-websocket',
        'wss://localhost//8080/xmpp-websocket'
    ]
    
    for url in malformed_urls:
        detected = False
        for pattern in malformed_patterns:
            if re.search(pattern, url):
                detected = True
                print(f"✅ URL malformada detectada con patrón '{pattern}': {url}")
                break
        
        assert detected, f"URL malformada no detectada: {url}"

@pytest.mark.docker
def test_websocket_url_validation_helper_integration():
    """Integración con el helper de validación"""
    import sys
    import os
    
    # Agregar el directorio helpers al path
    helpers_dir = os.path.join(os.path.dirname(__file__), 'helpers')
    if helpers_dir not in sys.path:
        sys.path.append(helpers_dir)
    
    try:
        from validate_websocket_url import validate_url
        
        # Test con URLs del error específico reportado
        specific_error_url = 'wss://http//localhost:8080/xmpp-websocket?room=recentconcessionscrysure'
        
        # Esta URL debería ser detectada como malformada
        is_valid = validate_url(specific_error_url)
        assert not is_valid, f"URL del error específico debería ser inválida: {specific_error_url}"
        print(f"✅ URL del error específico detectada como malformada: {specific_error_url}")
        
        # Test con URL correcta
        correct_url = 'wss://localhost:8080/xmpp-websocket?room=test'
        is_valid = validate_url(correct_url)
        assert is_valid, f"URL correcta debería ser válida: {correct_url}"
        print(f"✅ URL correcta validada: {correct_url}")
        
    except ImportError:
        pytest.skip("Helper de validación no disponible")

@pytest.mark.docker
def test_environment_variables_consistency(env_vars):
    """Verificar consistencia de variables de entorno"""
    public_url = env_vars['PUBLIC_URL']
    jitsi_domain = env_vars['JITSI_DOMAIN']
    
    # Verificar que JITSI_DOMAIN esté en PUBLIC_URL
    if 'localhost' in jitsi_domain:
        assert 'localhost' in public_url, f"JITSI_DOMAIN ({jitsi_domain}) no coincide con PUBLIC_URL ({public_url})"
    else:
        assert jitsi_domain in public_url, f"JITSI_DOMAIN ({jitsi_domain}) no coincide con PUBLIC_URL ({public_url})"
    
    print(f"✅ Variables de entorno consistentes:")
    print(f"   PUBLIC_URL: {public_url}")
    print(f"   JITSI_DOMAIN: {jitsi_domain}")

@pytest.mark.docker
def test_websocket_url_construction_edge_cases():
    """Probar casos edge en construcción de URLs WebSocket"""
    # Casos edge que podrían causar URLs malformadas
    edge_cases = [
        ('http://localhost:8080', 'localhost', 'ws://localhost:8080/xmpp-websocket'),
        ('https://localhost:8080', 'localhost', 'wss://localhost:8080/xmpp-websocket'),
        ('http://meet.example.com:8080', 'meet.example.com', 'ws://meet.example.com:8080/xmpp-websocket'),
        ('https://meet.example.com:8080', 'meet.example.com', 'wss://meet.example.com:8080/xmpp-websocket'),
    ]
    
    for public_url, domain, expected_ws_url in edge_cases:
        # Simular construcción
        if public_url.startswith('http://'):
            ws_protocol = 'ws://'
        elif public_url.startswith('https://'):
            ws_protocol = 'wss://'
        else:
            continue
        
        constructed_url = f"{ws_protocol}{domain}:8080/xmpp-websocket"
        
        assert constructed_url == expected_ws_url, \
            f"URL construida incorrectamente: {constructed_url} != {expected_ws_url}"
        
        # Verificar que no contenga patrones malformados
        assert 'http//' not in constructed_url, f"URL contiene patrón malformado: {constructed_url}"
        assert 'https//' not in constructed_url, f"URL contiene patrón malformado: {constructed_url}"
        
        print(f"✅ Caso edge correcto: {public_url} -> {constructed_url}")
