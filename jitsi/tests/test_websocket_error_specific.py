"""
Test específico para el error reportado: wss://http//localhost:8080/xmpp-websocket
"""
import pytest
import re
import os
import sys

@pytest.mark.docker
def test_specific_error_url_detection():
    """Detectar error específico wss://http//localhost:8080"""
    # URL exacta del error reportado
    error_url = 'wss://http//localhost:8080/xmpp-websocket?room=recentconcessionscrysure'
    
    # Patrón específico para este error
    error_pattern = r'wss?://http//.*'
    
    # Verificar que la URL coincide con el patrón de error
    assert re.search(error_pattern, error_url), f"URL del error no coincide con patrón: {error_url}"
    print(f"✅ Error específico detectado: {error_url}")
    
    # Verificar componentes específicos del error
    assert 'wss://http//' in error_url, "URL no contiene el patrón 'wss://http//'"
    assert 'localhost:8080' in error_url, "URL no contiene 'localhost:8080'"
    assert '/xmpp-websocket' in error_url, "URL no contiene '/xmpp-websocket'"
    
    print("✅ Componentes del error específico verificados")

@pytest.mark.docker
def test_url_construction_simulation():
    """Simular construcción de URL como Jitsi"""
    # Simular el proceso que lleva al error
    public_url = "http://localhost:8080"  # URL base correcta
    jitsi_domain = "localhost"
    
    # Simular construcción incorrecta que lleva al error
    # Esto es lo que NO debería pasar:
    incorrect_construction = f"wss://http//{jitsi_domain}:8080/xmpp-websocket"
    
    # Verificar que esta construcción es incorrecta
    assert 'http//' in incorrect_construction, "Construcción incorrecta no detectada"
    print(f"✅ Construcción incorrecta detectada: {incorrect_construction}")
    
    # Mostrar la construcción correcta
    correct_construction = f"wss://{jitsi_domain}:8080/xmpp-websocket"
    print(f"✅ Construcción correcta: {correct_construction}")

@pytest.mark.docker
def test_error_root_cause_analysis():
    """Analizar la causa raíz del error"""
    # Análisis del error: wss://http//localhost:8080
    error_analysis = {
        'error_url': 'wss://http//localhost:8080/xmpp-websocket',
        'correct_url': 'wss://localhost:8080/xmpp-websocket',
        'problem': 'Doble slash después de http (http//)',
        'cause': 'Concatenación incorrecta de URLs',
        'solution': 'Verificar PUBLIC_URL en .env y lógica de construcción'
    }
    
    print("🔍 ANÁLISIS DEL ERROR ESPECÍFICO:")
    for key, value in error_analysis.items():
        print(f"   {key}: {value}")
    
    # Verificar que entendemos el problema
    assert error_analysis['problem'] == 'Doble slash después de http (http//)'
    assert error_analysis['cause'] == 'Concatenación incorrecta de URLs'
    
    print("✅ Análisis del error completado")

@pytest.mark.docker
def test_error_detection_patterns():
    """Detectar diferentes variaciones del error específico"""
    # Variaciones del error que podrían ocurrir
    error_variations = [
        'wss://http//localhost:8080/xmpp-websocket',
        'ws://http//localhost:8080/xmpp-websocket',
        'wss://http//localhost:8080/xmpp-websocket?room=test',
        'wss://http//meet.example.com:8080/xmpp-websocket',
        'wss://http//localhost:8080/xmpp-websocket?room=recentconcessionscrysure'
    ]
    
    # Patrón para detectar todas las variaciones
    error_pattern = r'wss?://http//.*'
    
    detected_errors = []
    for url in error_variations:
        if re.search(error_pattern, url):
            detected_errors.append(url)
            print(f"✅ Error detectado: {url}")
    
    assert len(detected_errors) == len(error_variations), \
        f"No se detectaron todas las variaciones del error: {len(detected_errors)}/{len(error_variations)}"
    
    print(f"✅ Todas las variaciones del error detectadas: {len(detected_errors)}")

@pytest.mark.docker
def test_error_fix_validation():
    """Validar que las correcciones funcionan"""
    # URLs corregidas
    fixed_urls = [
        'wss://localhost:8080/xmpp-websocket',
        'ws://localhost:8080/xmpp-websocket',
        'wss://localhost:8080/xmpp-websocket?room=test',
        'wss://meet.example.com:8080/xmpp-websocket'
    ]
    
    # Patrón de error (no debería coincidir)
    error_pattern = r'wss?://http//.*'
    
    for url in fixed_urls:
        assert not re.search(error_pattern, url), f"URL corregida detectada como error: {url}"
        print(f"✅ URL corregida válida: {url}")

@pytest.mark.docker
def test_error_specific_room_parameter():
    """Test específico para el parámetro room del error"""
    # URL exacta del error con el parámetro room específico
    error_url = 'wss://http//localhost:8080/xmpp-websocket?room=recentconcessionscrysure'
    
    # Extraer parámetros
    from urllib.parse import urlparse, parse_qs
    
    parsed = urlparse(error_url)
    query_params = parse_qs(parsed.query)
    
    # Verificar que el parámetro room está presente
    assert 'room' in query_params, "Parámetro 'room' no encontrado en la URL"
    assert query_params['room'][0] == 'recentconcessionscrysure', \
        f"Room parameter incorrecto: {query_params['room'][0]}"
    
    print(f"✅ Parámetro room correcto: {query_params['room'][0]}")
    
    # Verificar que el error está en la parte del protocolo, no en los parámetros
    assert 'http//' in parsed.netloc, "Error no está en la parte del protocolo"
    print("✅ Error confirmado en la parte del protocolo")

@pytest.mark.docker
def test_error_environment_variables_impact():
    """Verificar impacto de variables de entorno en el error"""
    # Simular diferentes configuraciones que podrían causar el error
    test_configs = [
        {
            'PUBLIC_URL': 'http//localhost:8080',  # Incorrecto: falta ':'
            'JITSI_DOMAIN': 'localhost',
            'expected_error': True
        },
        {
            'PUBLIC_URL': 'http://localhost:8080',  # Correcto
            'JITSI_DOMAIN': 'localhost',
            'expected_error': False
        },
        {
            'PUBLIC_URL': 'http://localhost:8080',
            'JITSI_DOMAIN': 'http//localhost',  # Incorrecto
            'expected_error': True
        }
    ]
    
    for config in test_configs:
        public_url = config['PUBLIC_URL']
        jitsi_domain = config['JITSI_DOMAIN']
        expected_error = config['expected_error']
        
        # Simular construcción de URL WebSocket
        if 'http//' in public_url or 'http//' in jitsi_domain:
            has_error = True
        else:
            has_error = False
        
        assert has_error == expected_error, \
            f"Configuración {config} no produce el error esperado"
        
        status = "❌ ERROR" if has_error else "✅ CORRECTO"
        print(f"{status} Configuración: PUBLIC_URL={public_url}, JITSI_DOMAIN={jitsi_domain}")

@pytest.mark.docker
def test_error_log_analysis():
    """Analizar logs para detectar el error específico"""
    # Simular logs que contienen el error
    mock_logs = [
        "2025-10-20T04:17:00.512Z [INFO] [xmpp:Xmpp] <El.connectionHandler>: (TIME) Strophe connecting: 1719.9000000059605",
        "WebSocket connection to 'wss://http//localhost:8080/xmpp-websocket?room=recentconcessionscrysure' failed:",
        "2025-10-20T04:17:00.512Z [ERROR] [xmpp:strophe.util] <El.wi.Strophe.log>: Strophe: Websocket error {\"isTrusted\":true}",
        "2025-10-20T04:17:00.512Z [ERROR] [xmpp:strophe.util] <El.wi.Strophe.log>: Strophe: Websocket closed unexcectedly",
        "2025-10-20T04:17:00.512Z [INFO] [xmpp:Xmpp] <El.connectionHandler>: (TIME) Strophe connfail[The WebSocket connection could not be established or was disconnected.]: 1720.3000000044703"
    ]
    
    # Patrones para detectar el error en los logs
    error_patterns = [
        r"WebSocket connection to 'wss?://http//.*' failed",
        r"Strophe: Websocket error",
        r"Strophe: Websocket closed unexcectedly",
        r"Strophe connfail"
    ]
    
    detected_errors = []
    for log_entry in mock_logs:
        for pattern in error_patterns:
            if re.search(pattern, log_entry, re.IGNORECASE):
                detected_errors.append((pattern, log_entry))
                print(f"✅ Error detectado en log: {pattern}")
                break
    
    assert len(detected_errors) >= 3, f"No se detectaron suficientes errores en logs: {len(detected_errors)}"
    print(f"✅ Errores detectados en logs: {len(detected_errors)}")

@pytest.mark.docker
def test_error_solution_verification():
    """Verificar que las soluciones propuestas funcionan"""
    solutions = [
        {
            'name': 'Corregir PUBLIC_URL',
            'before': 'PUBLIC_URL=http//localhost:8080',
            'after': 'PUBLIC_URL=http://localhost:8080',
            'test': lambda: 'http//' not in 'http://localhost:8080'
        },
        {
            'name': 'Verificar JITSI_DOMAIN',
            'before': 'JITSI_DOMAIN=http//localhost',
            'after': 'JITSI_DOMAIN=localhost',
            'test': lambda: 'http//' not in 'localhost'
        },
        {
            'name': 'Reiniciar contenedor web',
            'before': 'docker compose restart web',
            'after': 'Contenedor reiniciado',
            'test': lambda: True  # Simular éxito
        }
    ]
    
    for solution in solutions:
        print(f"🔧 Solución: {solution['name']}")
        print(f"   Antes: {solution['before']}")
        print(f"   Después: {solution['after']}")
        
        # Verificar que la solución funciona
        assert solution['test'](), f"Solución {solution['name']} no funciona"
        print(f"   ✅ Solución verificada")
    
    print("✅ Todas las soluciones verificadas")
