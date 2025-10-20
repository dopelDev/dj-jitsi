#!/usr/bin/env python3
"""
Script helper para validar URLs WebSocket
Detecta patrones malformados como wss://http//localhost:8080
"""

import sys
import re
import json
from urllib.parse import urlparse

def validate_websocket_url(url):
    """
    Valida que una URL WebSocket esté correctamente formada
    
    Args:
        url (str): URL a validar
        
    Returns:
        tuple: (is_valid, message)
    """
    # Detectar patrones malformados comunes
    malformed_patterns = [
        (r'wss?://https?://', "Protocolo duplicado: wss://http://"),
        (r'wss?://https?//', "Protocolo duplicado con slash extra: wss://http//"),
        (r'://.*://', "Doble protocolo en cualquier parte"),
        (r'wss?://.*http', "Protocolo HTTP dentro de WebSocket"),
        (r'wss?://.*https', "Protocolo HTTPS dentro de WebSocket"),
    ]
    
    for pattern, description in malformed_patterns:
        if re.search(pattern, url):
            return False, f"URL malformada detectada: {description} (patrón: {pattern})"
    
    # Validar formato correcto de URL
    try:
        parsed = urlparse(url)
        
        # Verificar esquema
        if parsed.scheme not in ['ws', 'wss']:
            return False, f"Esquema inválido: {parsed.scheme}. Debe ser 'ws' o 'wss'"
        
        # Verificar que tenga hostname
        if not parsed.netloc:
            return False, "Falta hostname en la URL"
        
        # Verificar que no tenga caracteres problemáticos
        if '//' in parsed.netloc:
            return False, "Hostname contiene doble slash"
        
        return True, "URL WebSocket válida"
        
    except Exception as e:
        return False, f"Error al parsear URL: {str(e)}"

def analyze_websocket_config(config_text):
    """
    Analiza un texto de configuración buscando URLs WebSocket malformadas
    
    Args:
        config_text (str): Texto de configuración a analizar
        
    Returns:
        list: Lista de problemas encontrados
    """
    problems = []
    lines = config_text.split('\n')
    
    # Patrones a buscar en configuración
    websocket_patterns = [
        r'websocketUrl\s*[:=]\s*["\']([^"\']+)["\']',
        r'websocket\s*[:=]\s*["\']([^"\']+)["\']',
        r'bosh\s*[:=]\s*["\']([^"\']+)["\']',
        r'xmpp-websocket',
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern in websocket_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                # Validar cada URL encontrada
                if match and ('ws://' in match or 'wss://' in match):
                    is_valid, message = validate_websocket_url(match)
                    if not is_valid:
                        problems.append({
                            'line': i,
                            'content': line.strip(),
                            'url': match,
                            'problem': message
                        })
    
    return problems

def main():
    """Función principal del script"""
    if len(sys.argv) < 2:
        print("Uso: validate-websocket-url.py <url|--config-file> [archivo]")
        print("")
        print("Ejemplos:")
        print("  validate-websocket-url.py 'wss://localhost:8080/xmpp-websocket'")
        print("  validate-websocket-url.py --config-file config.js")
        sys.exit(1)
    
    if sys.argv[1] == "--config-file":
        if len(sys.argv) < 3:
            print("ERROR: Se requiere archivo de configuración")
            sys.exit(1)
        
        config_file = sys.argv[2]
        try:
            with open(config_file, 'r') as f:
                config_text = f.read()
            
            problems = analyze_websocket_config(config_text)
            
            if problems:
                print(f"❌ Se encontraron {len(problems)} problemas en {config_file}:")
                for problem in problems:
                    print(f"  Línea {problem['line']}: {problem['problem']}")
                    print(f"    URL: {problem['url']}")
                    print(f"    Contenido: {problem['content']}")
                    print("")
                sys.exit(1)
            else:
                print(f"✅ No se encontraron problemas en {config_file}")
                sys.exit(0)
        except FileNotFoundError:
            print(f"ERROR: Archivo no encontrado: {config_file}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    else:
        # Validar URL individual
        url = sys.argv[1]
        is_valid, message = validate_websocket_url(url)
        
        if is_valid:
            print(f"✅ {message}")
            sys.exit(0)
        else:
            print(f"❌ {message}")
            sys.exit(1)

if __name__ == "__main__":
    main()
